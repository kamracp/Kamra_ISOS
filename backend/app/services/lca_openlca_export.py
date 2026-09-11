"""openLCA JSON-LD (olca-schema v2) export for one LCA product.

Builds a zip openLCA 2.x can import: one UNIT_PROCESS per product, one
ELEMENTARY_FLOW per distinct factor reference, and a Kamra GWP impact method
whose characterisation factors are exactly the values the GWP engine resolved
(DEFRA / CEA / IPCC). A consultant can recalculate in openLCA and reproduce
the platform's kgCO2e per functional unit. Pure function -- no DB access.
"""
import io
import json
import uuid
import zipfile
from datetime import datetime, timezone

NS = uuid.UUID("6f1c2d3e-4b5a-4c6d-8e7f-90a1b2c3d4e5")  # fixed namespace -> stable ids across exports
VERSION = "01.00.000"


def _uid(kind: str, key) -> str:
    return str(uuid.uuid5(NS, f"kamra-isos:{kind}:{key}"))


def _ref(type_: str, id_: str, name: str) -> dict:
    return {"@type": type_, "@id": id_, "name": name}


def _entity(type_: str, id_: str, name: str, description: str = "") -> dict:
    return {"@type": type_, "@id": id_, "name": name, "description": description,
            "version": VERSION, "lastChange": datetime.now(timezone.utc).isoformat()}


def _unit_set(unit: str) -> tuple[dict, dict]:
    """UnitGroup + FlowProperty with `unit` as the sole reference unit (factor 1)."""
    ug_id, fp_id, u_id = _uid("unit_group", unit), _uid("flow_property", unit), _uid("unit", unit)
    ug = _entity("UnitGroup", ug_id, f"Units of {unit}")
    ug["units"] = [{"@type": "Unit", "@id": u_id, "name": unit, "conversionFactor": 1.0,
                    "isRefUnit": True, "referenceUnit": True}]
    ug["defaultFlowProperty"] = _ref("FlowProperty", fp_id, f"Quantity in {unit}")
    fp = _entity("FlowProperty", fp_id, f"Quantity in {unit}")
    fp["flowPropertyType"] = "PHYSICAL_QUANTITY"
    fp["unitGroup"] = _ref("UnitGroup", ug_id, ug["name"])
    return ug, fp


def _flow(id_: str, name: str, flow_type: str, unit: str, fp_id: str, description: str) -> dict:
    f = _entity("Flow", id_, name, description)
    f["flowType"] = flow_type
    f["flowProperties"] = [{"@type": "FlowPropertyFactor", "conversionFactor": 1.0,
                            "flowProperty": _ref("FlowProperty", fp_id, f"Quantity in {unit}"),
                            "isRefFlowProperty": True, "referenceFlowProperty": True}]
    return f


def _exchange(n: int, flow_id: str, name: str, unit: str, fp_id: str, amount: float,
              is_input: bool, is_ref: bool, stage: str | None = None) -> dict:
    e = {"@type": "Exchange", "internalId": n, "flow": _ref("Flow", flow_id, name),
         "flowProperty": _ref("FlowProperty", fp_id, f"Quantity in {unit}"),
         "unit": _ref("Unit", _uid("unit", unit), unit), "amount": amount,
         "isInput": is_input, "input": is_input,
         "isQuantitativeReference": is_ref, "quantitativeReference": is_ref}
    if stage:
        e["description"] = f"stage: {stage}"
    return e


def build_openlca_zip(p: dict) -> bytes:
    """p = LcaProductService.get_product() output (with items and by_stage)."""
    fu = p["functional_unit"]
    calc = [i for i in p["items"] if i["status"] == "calculated"]
    unresolved = [i for i in p["items"] if i["status"] != "calculated"]
    units = {fu} | {i["factor_unit"] for i in calc}
    unit_groups, flow_props = {}, {}
    for u in units:
        unit_groups[u], flow_props[u] = _unit_set(u)
    prod_flow_id = _uid("flow:product", p["id"])
    flows = {prod_flow_id: _flow(prod_flow_id, p["name"], "PRODUCT_FLOW", fu, flow_props[fu]["@id"],
                                 p.get("description") or "")}
    exchanges = [_exchange(1, prod_flow_id, p["name"], fu, flow_props[fu]["@id"],
                           p["functional_unit_qty"], False, True)]
    factors = {}
    for n, i in enumerate(calc, start=2):
        key = f"{i['factor_source']}:{i.get('fuel_key') or i.get('country_code') or i.get('emission_factor_id')}"
        fid, u = _uid("flow:input", key), i["factor_unit"]
        if fid not in flows:
            flows[fid] = _flow(fid, i["name"], "ELEMENTARY_FLOW", u, flow_props[u]["@id"],
                               f"Pre-aggregated fossil GWP factor {i['factor_value']} kgCO2e per {u} "
                               f"(biogenic CO2 excluded). Source: {i['factor_citation']}")
            factors[fid] = i
        exchanges.append(_exchange(n, fid, flows[fid]["name"], u, flow_props[u]["@id"],
                                   i["quantity_per_fu"], True, False, i["stage"]))
    desc = (f"Exported from Kamra ISOS LCA/PCF Studio. GWP {p['gwp_kgco2e_per_fu']} kgCO2e per "
            f"{p['functional_unit_qty']} {fu}. System boundary: {p['system_boundary']}. "
            f"Production country: {p['production_country_code']}. Reference year: {p.get('reference_year')}. ")
    if unresolved:
        desc += "NOT exported (unresolved): " + "; ".join(f"{i['name']} ({i['status']})" for i in unresolved)
    proc = _entity("Process", _uid("process", p["id"]), p["name"], desc)
    proc["processType"] = "UNIT_PROCESS"
    proc["exchanges"] = exchanges
    cat_id = _uid("impact_category", "gwp100")
    cat = _entity("ImpactCategory", cat_id, "Climate change - GWP 100 (Kamra, DEFRA/CEA/IPCC factors)")
    cat["referenceUnitName"] = "kg CO2-Eq"
    cat["impactFactors"] = [{"@type": "ImpactFactor", "flow": _ref("Flow", fid, flows[fid]["name"]),
                             "flowProperty": _ref("FlowProperty", flow_props[i["factor_unit"]]["@id"],
                                                  f"Quantity in {i['factor_unit']}"),
                             "unit": _ref("Unit", _uid("unit", i["factor_unit"]), i["factor_unit"]),
                             "value": i["factor_value"]} for fid, i in factors.items()]
    method = _entity("ImpactMethod", _uid("impact_method", "kamra_gwp"),
                     "Kamra ISOS GWP (fossil CO2e, pre-aggregated factors)")
    method["impactCategories"] = [_ref("ImpactCategory", cat_id, cat["name"])]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def put(folder: str, ent: dict) -> None:
            z.writestr(f"{folder}/{ent['@id']}.json", json.dumps(ent, indent=2))
        for ug in unit_groups.values():
            put("unit_groups", ug)
        for fp in flow_props.values():
            put("flow_properties", fp)
        for f in flows.values():
            put("flows", f)
        put("processes", proc)
        put("lca_categories", cat)
        put("lca_methods", method)
    return buf.getvalue()
