"""Scope 3 engine (GHG Protocol Value Chain Standard, 15 categories).

Nothing is stored: every call recomputes from source records and the current
emission_factors rows, so a factor revision recomputes all years.

  cat 3  derived  fuel records x DEFRA WTT factor (fuel_key -> wtt_* map);
                  electricity T&D losses need a sourced loss % per country (not
                  configured today -> not_computed, stated, never guessed)
  cat 4  entered  scope3_activity_records x cited factor (unit must match)
  cat 5  derived  waste records: SEBI material columns split by the record's
                  disposal-route mix, x DEFRA material/treatment factor
  others          not_tracked (listed, never zero)
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.emission_factor import EmissionFactor
from app.models.manufacturing_unit import ManufacturingUnit
from app.repositories.manufacturing_electricity_record_repository import ManufacturingElectricityRecordRepository
from app.repositories.manufacturing_fuel_record_repository import ManufacturingFuelRecordRepository
from app.repositories.scope3_repository import Scope3Repository
from app.repositories.waste_record_repository import WasteRecordRepository
from app.schemas.scope3 import Scope3RecordCreate, Scope3RecordUpdate
from app.services.country_config import get_country_config
from app.services.cross_sector_ef_library import get_fuel
from app.services.scope3_wtt_map import FUEL_WTT_METER_TYPE

CATEGORY_NAMES = {
    1: "Purchased goods and services", 2: "Capital goods", 3: "Fuel- and energy-related activities",
    4: "Upstream transportation and distribution", 5: "Waste generated in operations", 6: "Business travel",
    7: "Employee commuting", 8: "Upstream leased assets", 9: "Downstream transportation and distribution",
    10: "Processing of sold products", 11: "Use of sold products", 12: "End-of-life treatment of sold products",
    13: "Downstream leased assets", 14: "Franchises", 15: "Investments",
}
ENTERED = {1, 4, 6, 7, 9}   # session 2: cat 1 mat_*, cat 4/9 freight_*, cat 6/7 pass_* + wtt_pass_* (DEFRA passenger seed)
DERIVED = {3, 5}

# SEBI waste column -> DEFRA 'Waste disposal' Level-3 slug (name mapping only)
WASTE_MATERIAL = {
    "plastic_waste": "plastics_average_plastics", "e_waste": "weee_mixed",
    "construction_demolition_waste": "average_construction", "battery_waste": "batteries",
    "other_non_hazardous_waste": "commercial_and_industrial_waste",
    # no DEFRA row: bio_medical_waste, radioactive_waste, other_hazardous_waste -> gap
}
# disposal route column -> DEFRA treatment slug
WASTE_ROUTE = {"recycled": "closed_loop", "reused": "re_use", "other_recovery": "combustion",
               "incineration": "combustion", "landfilling": "landfill", "other_disposal": "landfill"}


def _f(v) -> float:
    return float(v) if v is not None else 0.0


class Scope3Service:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id
        self.repo = Scope3Repository(db, organization_id)
        self.fuel_repo = ManufacturingFuelRecordRepository(db, organization_id)
        self.elec_repo = ManufacturingElectricityRecordRepository(db, organization_id)
        self.waste_repo = WasteRecordRepository(db, organization_id)
        self._sources: list[str] = []

    # ---------------------------------------------------------------- factors
    def _factor_by_type(self, meter_type: str) -> EmissionFactor | None:
        return (self.db.query(EmissionFactor)
                .filter(EmissionFactor.meter_type == meter_type, EmissionFactor.is_active.is_(True))
                .order_by(EmissionFactor.valid_from.desc()).first())

    def _cite(self, ef: EmissionFactor) -> str:
        c = f"{ef.source} ({ef.source_year})" + (f": {ef.document_reference}" if ef.document_reference else "")
        if c not in self._sources:
            self._sources.append(c)
        return c

    # ---------------------------------------------------------------- cat 3
    def _cat3(self, year: int) -> dict:
        lines, gaps, total = [], [], 0.0
        for r in self.fuel_repo.get_all(year):
            mt = FUEL_WTT_METER_TYPE.get(r.fuel_key)
            ef = self._factor_by_type(mt) if mt else None
            name = (get_fuel(r.fuel_key) or {}).get("name", r.fuel_key)
            if ef is None:
                gaps.append(f"{name} {_f(r.quantity_tonnes):g} t ({r.period_start}): no DEFRA WTT mapping for '{r.fuel_key}'")
                continue
            t = _f(r.quantity_tonnes) * ef.factor_kgco2e_per_unit / 1000.0
            total += t
            lines.append({"source": f"WTT {name}", "period": str(r.period_start), "quantity": _f(r.quantity_tonnes), "unit": "tonne",
                          "factor_value": ef.factor_kgco2e_per_unit, "factor_unit": ef.unit, "factor_citation": self._cite(ef), "tco2e": round(t, 3)})
        elec = self.elec_repo.get_all(year)
        if elec:
            by_code: dict[str, float] = {}
            for e in elec:
                unit = self.db.get(ManufacturingUnit, e.manufacturing_unit_id) if e.manufacturing_unit_id else None
                code = (unit.country_code if unit and unit.country_code else None) or "IN"
                by_code[code] = by_code.get(code, 0.0) + _f(e.electricity_consumed_kwh)
            for code, kwh in sorted(by_code.items()):
                cc = get_country_config(code) or {}
                loss = cc.get("td_loss_fraction")
                if loss is None:
                    gaps.append(f"Electricity T&D losses: {kwh:,.0f} kWh in {code} not computed - no sourced T&D loss % configured for {code} (needs CEA/national source)")
                else:
                    t = kwh * loss * _f(cc.get("grid_factor_kgco2e_per_kwh")) / 1000.0
                    total += t
                    lines.append({"source": f"Electricity T&D losses ({code})", "quantity": kwh, "unit": "kWh", "factor_value": loss,
                                  "factor_unit": "loss fraction", "factor_citation": cc.get("td_loss_source", ""), "tco2e": round(t, 3)})
        return self._pack(3, "derived", lines, gaps, total)

    # ---------------------------------------------------------------- cat 4
    def _entered(self, cat: int, year: int) -> dict:
        """Any entered category: activity records x cited factor; calc_record enforces unit match."""
        lines, gaps, total = [], [], 0.0
        for r in self.repo.get_all(year, cat):
            row = self.calc_record(r)
            if row["status"] != "calculated":
                gaps.append(f"{r.description}: {row['status_reason']}")
                continue
            total += row["tco2e"]
            lines.append({"source": r.description, "quantity": r.quantity, "unit": r.unit, "factor_value": row["factor_value"],
                          "factor_unit": row["factor_unit"], "factor_citation": row["factor_citation"], "tco2e": row["tco2e"]})
        return self._pack(cat, "entered", lines, gaps, total)

    # ---------------------------------------------------------------- cat 5
    def _cat5(self, year: int) -> dict:
        lines, gaps, total = [], [], 0.0
        for w in self.waste_repo.get_all(year):
            routes = {k: _f(getattr(w, k)) for k in WASTE_ROUTE}
            route_total = sum(routes.values())
            materials = {k: _f(getattr(w, k)) for k in ("plastic_waste", "e_waste", "bio_medical_waste", "construction_demolition_waste",
                                                         "battery_waste", "radioactive_waste", "other_hazardous_waste", "other_non_hazardous_waste")}
            if route_total <= 0:
                if sum(materials.values()) > 0:
                    gaps.append(f"Waste record {w.period_start}: no disposal-route tonnes entered, cannot allocate treatment")
                continue
            for mat, tonnes in materials.items():
                if tonnes <= 0:
                    continue
                mslug = WASTE_MATERIAL.get(mat)
                if mslug is None:
                    gaps.append(f"{mat.replace('_', ' ')} {tonnes:g} t ({w.period_start}): no DEFRA treatment factor for this SEBI category")
                    continue
                for route, rt in routes.items():
                    if rt <= 0:
                        continue
                    share = tonnes * rt / route_total
                    mt = f"waste_{mslug}_{WASTE_ROUTE[route]}"
                    ef = self._factor_by_type(mt)
                    if ef is None and route == "recycled":          # DEFRA has open-loop only for some materials
                        mt = f"waste_{mslug}_open_loop"
                        ef = self._factor_by_type(mt)
                    if ef is None:
                        gaps.append(f"{mat.replace('_', ' ')} via {route} {share:.3f} t: no DEFRA row '{mt}'")
                        continue
                    t = share * ef.factor_kgco2e_per_unit / 1000.0
                    total += t
                    lines.append({"source": f"{mat.replace('_', ' ')} via {route.replace('_', ' ')}", "period": str(w.period_start), "quantity": round(share, 3),
                                  "unit": "tonne", "factor_value": ef.factor_kgco2e_per_unit, "factor_unit": ef.unit, "factor_citation": self._cite(ef), "tco2e": round(t, 3)})
        return self._pack(5, "derived", lines, gaps, total)

    # ---------------------------------------------------------------- common
    def _pack(self, cat: int, basis: str, lines: list, gaps: list, total: float) -> dict:
        if not lines and not gaps:
            status, reason, val = "not_computed", "no source records for this year", None
        elif not lines:
            status, reason, val = "not_computed", "; ".join(gaps[:3]), None
        elif gaps:
            status, reason, val = "partial", f"{len(gaps)} line(s) not computed - see gaps", round(total, 3)
        else:
            status, reason, val = "calculated", None, round(total, 3)
        return {"category": cat, "name": CATEGORY_NAMES[cat], "basis": basis, "status": status, "status_reason": reason,
                "tco2e": val, "lines": lines, "gaps": gaps}

    def calc_record(self, r) -> dict:
        out = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        out.update({"status": "pending", "status_reason": None, "factor_value": None, "factor_unit": None, "factor_citation": None, "tco2e": None})
        ef = r.emission_factor
        if ef is None or not ef.is_active:
            out.update(status="no_factor", status_reason="emission factor missing or inactive"); return out
        if (r.unit or "").strip().lower() != (ef.unit or "").strip().lower():
            out.update(status="unit_mismatch", status_reason=f"record unit '{r.unit}' != factor unit '{ef.unit}'"); return out
        out.update(status="calculated", factor_value=ef.factor_kgco2e_per_unit, factor_unit=ef.unit, factor_citation=self._cite(ef),
                   tco2e=round(r.quantity * ef.factor_kgco2e_per_unit / 1000.0, 3))
        return out

    def summary(self, year: int) -> dict:
        self._sources = []
        cats = {3: self._cat3(year), 5: self._cat5(year)}
        for c in sorted(ENTERED):
            cats[c] = self._entered(c, year)
        out = []
        for c in range(1, 16):
            out.append(cats.get(c) or {"category": c, "name": CATEGORY_NAMES[c], "basis": "not_tracked", "status": "not_tracked",
                                       "status_reason": "not tracked on the platform yet", "tco2e": None, "lines": [], "gaps": []})
        vals = [c["tco2e"] for c in out if c["tco2e"] is not None]
        return {"year": year, "total_tco2e": round(sum(vals), 3) if vals else None, "computed_categories": len(vals),
                "categories": out, "factor_sources": list(self._sources)}

    # ---------------------------------------------------------------- CRUD
    def list_records(self, year: int | None = None, category: int | None = None) -> list[dict]:
        return [self.calc_record(r) for r in self.repo.get_all(year, category)]

    def get_record(self, rid: int) -> dict | None:
        r = self.repo.get_by_id(rid); return self.calc_record(r) if r else None

    def create_record(self, data: Scope3RecordCreate) -> dict:
        return self.calc_record(self.repo.get_by_id(self.repo.create(data).id))

    def update_record(self, rid: int, data: Scope3RecordUpdate) -> dict | None:
        r = self.repo.get_by_id(rid)
        if r is None:
            return None
        self.repo.update(r, data); return self.calc_record(self.repo.get_by_id(rid))

    def delete_record(self, rid: int) -> bool:
        r = self.repo.get_by_id(rid)
        if r is None:
            return False
        self.repo.delete(r); return True
