"""Pydantic schemas for CBAM goods. Computed SEE fields live on the response only."""
from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

GoodsCategory = Literal["cement", "iron_steel", "aluminium", "fertilisers", "hydrogen", "electricity"]

_CN = re.compile(r"^\d{4,8}$")


def _check_cn(v: str) -> str:
    digits = v.replace(" ", "").replace(".", "")
    if not _CN.match(digits):
        raise ValueError("cn_code must be 4-8 digits (Combined Nomenclature), e.g. '2523 29 00'")
    return " ".join([digits[:4], digits[4:6], digits[6:8]]).strip() if len(digits) > 4 else digits


class CbamGoodBase(BaseModel):
    manufacturing_unit_id: int | None = None
    lca_product_id: int | None = None
    name: str = Field(..., max_length=200)
    cn_code: str = Field(..., max_length=12)
    goods_category: GoodsCategory
    production_route: str | None = Field(None, max_length=120)
    reporting_year: int = Field(..., ge=2026, le=2100)
    production_qty_tonne: float = Field(..., ge=0)
    carbon_price_paid_per_tco2e: float | None = Field(None, ge=0)
    remarks: str | None = None

    @field_validator("cn_code")
    @classmethod
    def cn_valid(cls, v: str) -> str:
        return _check_cn(v)


class CbamGoodCreate(CbamGoodBase):
    pass


class CbamGoodUpdate(BaseModel):
    manufacturing_unit_id: int | None = None
    lca_product_id: int | None = None
    name: str | None = Field(None, max_length=200)
    cn_code: str | None = Field(None, max_length=12)
    goods_category: GoodsCategory | None = None
    production_route: str | None = Field(None, max_length=120)
    reporting_year: int | None = Field(None, ge=2026, le=2100)
    production_qty_tonne: float | None = Field(None, ge=0)
    carbon_price_paid_per_tco2e: float | None = Field(None, ge=0)
    remarks: str | None = None

    @field_validator("cn_code")
    @classmethod
    def cn_valid(cls, v: str | None) -> str | None:
        return None if v is None else _check_cn(v)


class CbamGoodResponse(CbamGoodBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organization_id: int
    # Computed at read time by the CBAM engine (never stored):
    indirect_required: bool = True
    status: str = "pending"          # calculated | no_lca | fu_not_mass | lca_unresolved
    status_reason: str | None = None
    see_direct_tco2e_per_t: float | None = None
    see_indirect_tco2e_per_t: float | None = None
    see_total_tco2e_per_t: float | None = None
    total_embedded_tco2e: float | None = None       # SEE total x production_qty_tonne
    excluded_items: list[str] = []                   # LCA items outside the CBAM boundary
    factor_sources: list[str] = []
