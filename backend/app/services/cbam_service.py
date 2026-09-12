"""
CBAM engine: re-cuts an LcaProduct's resolved inventory along CBAM boundaries
and returns specific embedded emissions (SEE) in tCO2e per tonne of good.
Nothing is persisted; the LCA engine remains the single calculation path.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.cbam_good import CbamGood, INDIRECT_REQUIRED
from app.repositories.cbam_good_repository import CbamGoodRepository
from app.schemas.cbam_good import CbamGoodCreate, CbamGoodUpdate
from app.services.lca_product_service import LcaProductService

_MASS_TO_TONNE = {"tonne": 1.0, "t": 1.0, "mt": 1.0, "kg": 0.001}
# emission_factors rows that are PROCESS emissions (IPCC Vol.3): direct under CBAM,
# even though the LCA engine reaches them through factor_source == "factor".
PROCESS_METER_TYPES = {"clinker_calcination", "carbon_anode"}


def _row(obj) -> dict:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


class CbamService:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id
        self.repo = CbamGoodRepository(db, organization_id)
        self.lca = LcaProductService(db, organization_id)

    def _calc(self, good: CbamGood) -> dict:
        out = _row(good)
        out.update({"indirect_required": INDIRECT_REQUIRED[good.goods_category], "status": "pending",
                    "status_reason": None, "see_direct_tco2e_per_t": None, "see_indirect_tco2e_per_t": None,
                    "see_total_tco2e_per_t": None, "total_embedded_tco2e": None,
                    "excluded_items": [], "factor_sources": []})
        if good.lca_product_id is None:
            out.update(status="no_lca", status_reason="link an LCA product (functional unit: 1 tonne or kg of the good)")
            return out
        p = self.lca.get_product(good.lca_product_id)
        if p is None:
            out.update(status="no_lca", status_reason=f"LCA product {good.lca_product_id} not found")
            return out
        fu_factor = _MASS_TO_TONNE.get((p["functional_unit"] or "").strip().lower())
        if fu_factor is None:
            out.update(status="fu_not_mass", status_reason=f"functional unit '{p['functional_unit']}' is not a mass unit; CBAM needs tCO2e per tonne")
            return out
        unresolved = [i["name"] for i in p["items"] if i["status"] != "calculated"]
        if unresolved:
            out.update(status="lca_unresolved", status_reason="unresolved LCA items: " + ", ".join(unresolved))
            return out
        tonnes_per_fu = p["functional_unit_qty"] * fu_factor
        def is_process(i: dict) -> bool:
            if i["factor_source"] != "factor" or not i.get("emission_factor_id"):
                return False
            ef = self.lca.factor_repo.get_by_id(i["emission_factor_id"])
            return ef is not None and ef.meter_type in PROCESS_METER_TYPES
        direct = sum(i["co2e_kg_per_fu"] for i in p["items"] if i["factor_source"] == "fuel" or is_process(i))
        indirect = sum(i["co2e_kg_per_fu"] for i in p["items"] if i["factor_source"] == "electricity")
        out["excluded_items"] = [f"{i['name']} ({i['co2e_kg_per_fu']} kgCO2e/FU, outside CBAM boundary unless precursor)"
                                 for i in p["items"] if i["factor_source"] == "factor" and not is_process(i)]
        see_d = direct / 1000.0 / tonnes_per_fu
        see_i = indirect / 1000.0 / tonnes_per_fu
        see_t = see_d + (see_i if out["indirect_required"] else 0.0)
        out.update(status="calculated", see_direct_tco2e_per_t=round(see_d, 6), see_indirect_tco2e_per_t=round(see_i, 6),
                   see_total_tco2e_per_t=round(see_t, 6), total_embedded_tco2e=round(see_t * good.production_qty_tonne, 3),
                   factor_sources=p["factor_sources"])
        if not out["indirect_required"] and indirect > 0:
            out["status_reason"] = "Annex II good: indirect emissions reported but not counted in SEE total"
        return out

    def list_goods(self, year: int | None = None) -> list[dict]:
        return [self._calc(g) for g in self.repo.get_all(year)]

    def get_good(self, good_id: int) -> dict | None:
        g = self.repo.get_by_id(good_id)
        return None if g is None else self._calc(g)

    def create_good(self, data: CbamGoodCreate) -> dict:
        return self._calc(self.repo.create(data))

    def update_good(self, good_id: int, data: CbamGoodUpdate) -> dict | None:
        g = self.repo.get_by_id(good_id)
        return None if g is None else self._calc(self.repo.update(g, data))

    def delete_good(self, good_id: int) -> bool:
        g = self.repo.get_by_id(good_id)
        if g is None:
            return False
        self.repo.delete(g)
        return True
