"""Material Circularity Indicator (MCI) - Ellen MacArthur Foundation, Circularity Indicators
methodology v1.1 (2019), product level, mass basis, per functional unit.

  V  = M (1 - Fr - Fu)              virgin feedstock
  W0 = M (1 - Cr - Cu)              unrecoverable waste (landfill / energy recovery)
  Wc = M (1 - Ec) Cr                waste from end-of-life recycling
  Wf = M (1 - Ef) Fr / Ef           waste generated producing recycled feedstock
  W  = W0 + (Wf + Wc) / 2
  LFI = (V + W) / (2M + (Wf - Wc) / 2)
  F(X) = 0.9 / X,  X = L / Lav      (utility; U/Uav not modelled -> 1)
  MCI = max(0, 1 - LFI * F(X))

Conventions (never defaults): M counts raw_materials items with a mass unit and a non-fuel
source; Fr / Fu are mass-weighted over those items and each must be stated; Cr and Cu must be
stated; Ef is required when Fr > 0, Ec when Cr > 0. If neither L nor Lav is given, X = 1 and
the output says so explicitly. Any other missing input -> not_computed with the reason.
"""
_MASS_TO_KG = {"kg": 1.0, "kgs": 1.0, "tonne": 1000.0, "tonnes": 1000.0, "t": 1000.0, "mt": 1000.0, "g": 0.001}


def _per_fu(item, product) -> float | None:
    if item.basis == "annual_total":
        if not product.annual_output_qty:
            return None
        return item.quantity * product.functional_unit_qty / product.annual_output_qty
    return item.quantity


def compute_mci(product, items) -> dict:
    counted, excluded, missing = [], [], []
    for it in items:
        if it.stage != "raw_materials":
            continue
        if it.factor_source == "fuel":
            excluded.append(f"{it.name}: fuel, not product material"); continue
        k = _MASS_TO_KG.get((it.unit or "").strip().lower())
        if k is None:
            excluded.append(f"{it.name}: unit '{it.unit}' is not a mass unit"); continue
        q = _per_fu(it, product)
        if q is None:
            excluded.append(f"{it.name}: annual_total basis but product has no annual output"); continue
        if it.recycled_content_fraction is None or it.reused_content_fraction is None:
            missing.append(f"{it.name}: recycled/reused content fraction not stated")
        counted.append((it.name, q * k, it.recycled_content_fraction, it.reused_content_fraction))
    out = {"status": "not_computed", "reason": None, "mass_kg_per_fu": None, "items_counted": [c[0] for c in counted],
           "items_excluded": excluded}
    if not counted:
        out["reason"] = "no raw_materials items with a mass unit"; return out
    if missing:
        out["reason"] = "; ".join(missing); return out
    m = sum(c[1] for c in counted)
    if m <= 0:
        out["reason"] = "total material mass is zero"; return out
    fr = sum(c[1] * c[2] for c in counted) / m
    fu = sum(c[1] * c[3] for c in counted) / m
    if fr + fu > 1.0 + 1e-9:
        out["reason"] = f"recycled + reused content = {fr + fu:.3f} > 1"; return out
    cr, cu, ef, ec = product.eol_recycling_fraction, product.eol_reuse_fraction, product.recycling_efficiency_input, product.recycling_efficiency_eol
    if cr is None or cu is None:
        out["reason"] = "end-of-life recycling / reuse fractions not stated on the product"; return out
    if cr + cu > 1.0 + 1e-9:
        out["reason"] = f"EoL recycling + reuse = {cr + cu:.3f} > 1"; return out
    if fr > 0 and not ef:
        out["reason"] = "recycling_efficiency_input (Ef) required when recycled content > 0"; return out
    if cr > 0 and ec is None:
        out["reason"] = "recycling_efficiency_eol (Ec) required when EoL recycling > 0"; return out
    l, lav = product.lifetime_years, product.industry_avg_lifetime_years
    if l is None and lav is None:
        x, note = 1.0, "utility factor X = 1: lifetime and industry-average lifetime not given"
    elif l is None or lav is None:
        out["reason"] = "both lifetime_years and industry_avg_lifetime_years are needed for the utility factor"; return out
    else:
        x, note = l / lav, f"utility factor X = L/Lav = {l:g}/{lav:g}"
    v = m * (1 - fr - fu)
    w0 = m * (1 - cr - cu)
    wc = m * (1 - (ec or 0.0)) * cr
    wf = m * (1 - ef) * fr / ef if fr > 0 else 0.0
    w = w0 + (wf + wc) / 2
    lfi = (v + w) / (2 * m + (wf - wc) / 2)
    fx = 0.9 / x
    mci = max(0.0, 1 - lfi * fx)
    out.update({"status": "calculated", "mass_kg_per_fu": round(m, 6), "fr": round(fr, 4), "fu": round(fu, 4), "cr": cr, "cu": cu,
                "ef": ef, "ec": ec, "x": round(x, 4), "utility_note": note, "virgin_kg": round(v, 6), "waste_kg": round(w, 6),
                "lfi": round(lfi, 4), "mci": round(mci, 4),
                "method": "Ellen MacArthur Foundation, Circularity Indicators methodology v1.1 (2019), mass basis per functional unit"})
    return out
