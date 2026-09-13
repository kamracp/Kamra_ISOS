"""
LCA/PCF Studio service: product + inventory CRUD and the GWP engine.

Engine (per item):
  factor  <- resolved at read time from fuel library / country grid /
             emission_factors row (never stored)
  qty_fu  <- quantity, or annual_total x functional_unit_qty / annual_output_qty
  co2e    <- qty_fu x factor_kgco2e_per_unit        (fossil)
  biogenic<- qty_fu x (total - fossil) for biomass fuels, reported separately
Units must match the factor's unit exactly; no silent conversion.
Per-product and per-stage totals are sums of *calculated* items only and are
None (not 0) when nothing could be calculated.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.lca_mci import compute_mci
from app.services.lca_benchmarks import benchmark_check
from app.models.lca_product import LcaProduct, LcaInventoryItem, LCA_STAGES
from app.repositories.lca_product_repository import LcaProductRepository
from app.repositories.emission_factor_repository import EmissionFactorRepository
from app.schemas.lca_product import (
    LcaProductCreate, LcaProductUpdate,
    LcaInventoryItemCreate, LcaInventoryItemUpdate,
    check_factor_reference,
)
from app.services.cross_sector_ef_library import get_fuel, co2e_per_tonne, is_biogenic
from app.services.country_config import get_country_config

FUEL_CITATION = "IPCC 2006 Vol.2 Ch.2 (AR5 GWP-100)"
_UNIT_ALIASES = {"t": "tonne", "tonnes": "tonne", "mt": "tonne", "kwh": "kWh", "kgs": "kg"}


def _norm_unit(u: str | None) -> str | None:
    if u is None:
        return None
    s = u.strip()
    return _UNIT_ALIASES.get(s.lower(), s if s.lower() != "kwh" else "kWh")


def _row(obj) -> dict:
    """Plain dict of an ORM row's own columns (no relationships)."""
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


class LcaProductService:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id
        self.repo = LcaProductRepository(db, organization_id)
        self.factor_repo = EmissionFactorRepository(db)

    # ------------------------------------------------------------ engine ---

    def _resolve_factor(self, item: LcaInventoryItem) -> dict:
        """Returns factor_value (fossil kgCO2e/unit), factor_unit, citation,
        is_biogenic, biogenic_value; or status no_factor with a reason."""
        if item.factor_source == "fuel":
            f = get_fuel(item.fuel_key)
            fossil = co2e_per_tonne(item.fuel_key, include_biogenic_co2=False)
            total = co2e_per_tonne(item.fuel_key, include_biogenic_co2=True)
            if f is None or fossil is None:
                return {"status": "no_factor", "reason": f"fuel '{item.fuel_key}' has no LHV/factor"}
            bio = is_biogenic(item.fuel_key)
            return {
                "status": "ok", "factor_value": fossil, "factor_unit": "tonne",
                "factor_citation": f"{FUEL_CITATION}: {f.get('name')}",
                "is_biogenic": bio,
                "biogenic_value": round(total - fossil, 4) if (bio and total is not None) else 0.0,
            }
        if item.factor_source == "electricity":
            cc = get_country_config(item.country_code)
            if cc is None or cc.get("grid_factor_kgco2e_per_kwh") is None:
                return {"status": "no_factor", "reason": f"no verified grid factor for '{item.country_code}'"}
            return {
                "status": "ok", "factor_value": cc["grid_factor_kgco2e_per_kwh"], "factor_unit": "kWh",
                "factor_citation": cc.get("grid_factor_source") or f"grid factor {item.country_code}",
                "is_biogenic": False, "biogenic_value": 0.0,
            }
        ef = self.factor_repo.get_by_id(item.emission_factor_id)
        if ef is None:
            return {"status": "no_factor", "reason": f"emission_factor {item.emission_factor_id} not found"}
        if not ef.is_active:
            return {"status": "no_factor", "reason": f"emission_factor {ef.id} is inactive"}
        cite = f"{ef.source} {ef.source_year}"
        if ef.document_reference:
            cite += f" ({ef.document_reference})"
        return {
            "status": "ok", "factor_value": ef.factor_kgco2e_per_unit, "factor_unit": ef.unit,
            "factor_citation": cite, "is_biogenic": False, "biogenic_value": 0.0,
        }

    def _calc_item(self, item: LcaInventoryItem, product: LcaProduct) -> dict:
        out = _row(item)
        out.update({"status": "pending", "quantity_per_fu": None, "factor_value": None,
                    "factor_unit": None, "factor_citation": None, "is_biogenic": False,
                    "co2e_kg_per_fu": None, "biogenic_co2_kg_per_fu": None})
        fr = self._resolve_factor(item)
        if fr["status"] != "ok":
            out["status"] = "no_factor"
            out["factor_citation"] = fr.get("reason")
            return out
        out.update({"factor_value": fr["factor_value"], "factor_unit": fr["factor_unit"],
                    "factor_citation": fr["factor_citation"], "is_biogenic": fr["is_biogenic"]})
        if _norm_unit(item.unit) != _norm_unit(fr["factor_unit"]):
            out["status"] = "unit_mismatch"
            return out
        if item.basis == "annual_total":
            if not product.annual_output_qty:
                out["status"] = "no_annual_output"
                return out
            qty_fu = item.quantity * product.functional_unit_qty / product.annual_output_qty
        else:
            qty_fu = item.quantity
        out["quantity_per_fu"] = round(qty_fu, 6)
        out["co2e_kg_per_fu"] = round(qty_fu * fr["factor_value"], 6)
        out["biogenic_co2_kg_per_fu"] = round(qty_fu * fr["biogenic_value"], 6) if fr["is_biogenic"] else 0.0
        out["status"] = "calculated"
        return out

    def _calc_product(self, product: LcaProduct, with_items: bool = True) -> dict:
        out = _row(product)
        items = [self._calc_item(i, product) for i in product.items]
        calc = [i for i in items if i["status"] == "calculated"]
        gwp = round(sum(i["co2e_kg_per_fu"] for i in calc), 6) if calc else None
        out.update({
            "item_count": len(items),
            "unresolved_count": len(items) - len(calc),
            "gwp_kgco2e_per_fu": gwp,
        })
        out["benchmark"] = benchmark_check(product.benchmark_key, product.functional_unit, gwp)
        if not with_items:
            return out
        by_stage = []
        for stage in LCA_STAGES:
            s_all = [i for i in items if i["stage"] == stage]
            s_calc = [i for i in s_all if i["status"] == "calculated"]
            s_tot = round(sum(i["co2e_kg_per_fu"] for i in s_calc), 6) if s_calc else None
            by_stage.append({
                "stage": stage, "item_count": len(s_all), "co2e_kg_per_fu": s_tot,
                "share_percent": round(100.0 * s_tot / gwp, 2) if (s_tot is not None and gwp) else None,
            })
        out.update({
            "items": items,
            "by_stage": by_stage,
            "biogenic_co2_kg_per_fu": round(sum(i["biogenic_co2_kg_per_fu"] or 0.0 for i in calc), 6) if calc else None,
            "factor_sources": sorted({i["factor_citation"] for i in calc if i["factor_citation"]}),
        })
        out["mci"] = compute_mci(product, product.items)
        return out

    # ---------------------------------------------------------- products ---

    def list_products(self, year: int | None = None) -> list[dict]:
        return [self._calc_product(p, with_items=False) for p in self.repo.get_all(year)]

    def get_product(self, product_id: int) -> dict | None:
        p = self.repo.get_by_id(product_id)
        return None if p is None else self._calc_product(p)

    def create_product(self, data: LcaProductCreate) -> dict:
        return self._calc_product(self.repo.create(data))

    def update_product(self, product_id: int, data: LcaProductUpdate) -> dict | None:
        p = self.repo.get_by_id(product_id)
        return None if p is None else self._calc_product(self.repo.update(p, data))

    def delete_product(self, product_id: int) -> bool:
        p = self.repo.get_by_id(product_id)
        if p is None:
            return False
        self.repo.delete(p)
        return True

    # ------------------------------------------------------------- items ---

    def _check_emission_factor_exists(self, factor_id: int | None) -> None:
        if factor_id is not None and self.factor_repo.get_by_id(factor_id) is None:
            raise ValueError(f"emission_factor_id {factor_id} does not exist")

    def add_item(self, product_id: int, data: LcaInventoryItemCreate) -> dict | None:
        p = self.repo.get_by_id(product_id)
        if p is None:
            return None
        self._check_emission_factor_exists(data.emission_factor_id)
        self.repo.create_item(p, data)
        return self.get_product(product_id)

    def update_item(self, product_id: int, item_id: int, data: LcaInventoryItemUpdate) -> dict | None:
        item = self.repo.get_item(product_id, item_id)
        if item is None:
            return None
        merged = _row(item)
        patch = data.model_dump(exclude_unset=True)
        merged.update(patch)
        # If the source changed, drop the references that no longer apply so the
        # caller need not null them explicitly.
        if "factor_source" in patch:
            for src, col in (("fuel", "fuel_key"), ("electricity", "country_code"), ("factor", "emission_factor_id")):
                if src != merged["factor_source"] and col not in patch:
                    merged[col] = None
        check_factor_reference(merged["factor_source"], merged["fuel_key"],
                               merged["country_code"], merged["emission_factor_id"])
        self._check_emission_factor_exists(merged["emission_factor_id"])
        update_data = {k: merged[k] for k in set(patch) | {"fuel_key", "country_code", "emission_factor_id"}}
        self.repo.update_item(item, update_data)
        return self.get_product(product_id)

    def delete_item(self, product_id: int, item_id: int) -> dict | None:
        item = self.repo.get_item(product_id, item_id)
        if item is None:
            return None
        self.repo.delete_item(item)
        return self.get_product(product_id)
