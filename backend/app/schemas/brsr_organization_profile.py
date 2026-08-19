from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional, List

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Nested block models.
#
# These are stored as JSONB in the DB (loose storage) but validated strictly
# here at the API boundary, so malformed disclosure blocks are rejected on
# entry rather than discovered at report-generation time.
# ---------------------------------------------------------------------------


class BusinessActivity(BaseModel):
    """BRSR Section A, Q14."""
    description: str
    nic_code: Optional[str] = None
    turnover_percent: Optional[float] = Field(default=None, ge=0, le=100)


class ProductSold(BaseModel):
    """BRSR Section A, Q15."""
    product_service: str
    nic_code: Optional[str] = None
    turnover_percent: Optional[float] = Field(default=None, ge=0, le=100)


class LocationSplit(BaseModel):
    national: int = Field(default=0, ge=0)
    international: int = Field(default=0, ge=0)


class LocationCounts(BaseModel):
    """BRSR Section A, Q16."""
    plants: LocationSplit = Field(default_factory=LocationSplit)
    offices: LocationSplit = Field(default_factory=LocationSplit)


class MarketsServed(BaseModel):
    """BRSR Section A, Q17."""
    national_states: Optional[int] = Field(default=None, ge=0)
    international_countries: Optional[int] = Field(default=None, ge=0)
    exports_percent: Optional[float] = Field(default=None, ge=0, le=100)
    customer_types: Optional[str] = None


class GenderSplit(BaseModel):
    total: int = Field(default=0, ge=0)
    male: int = Field(default=0, ge=0)
    female: int = Field(default=0, ge=0)


class CategorySplit(BaseModel):
    permanent: GenderSplit = Field(default_factory=GenderSplit)
    other: GenderSplit = Field(default_factory=GenderSplit)


class EmployeeWorkerCounts(BaseModel):
    """BRSR Section A, Q18 / Q18b (same shape for differently abled)."""
    employees: CategorySplit = Field(default_factory=CategorySplit)
    workers: CategorySplit = Field(default_factory=CategorySplit)


class WomenParticipation(BaseModel):
    """BRSR Section A, Q19."""
    board_total: Optional[int] = Field(default=None, ge=0)
    board_female: Optional[int] = Field(default=None, ge=0)
    kmp_total: Optional[int] = Field(default=None, ge=0)
    kmp_female: Optional[int] = Field(default=None, ge=0)


class TurnoverRate(BaseModel):
    """BRSR Section A, Q20. One row per year per category."""
    year: str
    category: str
    male_turnover_percent: Optional[float] = Field(default=None, ge=0, le=100)
    female_turnover_percent: Optional[float] = Field(default=None, ge=0, le=100)
    total_turnover_percent: Optional[float] = Field(default=None, ge=0, le=100)


class GroupCompany(BaseModel):
    """BRSR Section A, Q21."""
    name: str
    relationship: str  # holding / subsidiary / associate / joint venture
    shareholding_percent: Optional[float] = Field(default=None, ge=0, le=100)
    participates_in_brsr: Optional[bool] = None


class GrievanceEntry(BaseModel):
    """BRSR Section A, Q23. One row per stakeholder group."""
    stakeholder_group: str
    grievance_mechanism: Optional[str] = None
    filed_current_year: int = Field(default=0, ge=0)
    pending_current_year: int = Field(default=0, ge=0)
    filed_previous_year: int = Field(default=0, ge=0)
    pending_previous_year: int = Field(default=0, ge=0)


# ---------------------------------------------------------------------------
# Main profile schemas
# ---------------------------------------------------------------------------


class BrsrOrganizationProfileBase(BaseModel):
    # A.I Details of the listed entity
    cin: Optional[str] = None
    year_of_incorporation: Optional[int] = Field(default=None, ge=1800, le=2100)
    registered_office_address: Optional[str] = None
    corporate_address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_telephone: Optional[str] = None
    website: Optional[str] = None
    financial_year_reported: Optional[str] = None
    stock_exchanges_listed: Optional[List[str]] = None
    paid_up_capital_inr: Optional[Decimal] = Field(default=None, ge=0)
    brsr_contact_name: Optional[str] = None
    brsr_contact_phone: Optional[str] = None
    brsr_contact_email: Optional[str] = None
    reporting_boundary: Optional[Literal["standalone", "consolidated"]] = None

    # A.II Products and services
    business_activities: Optional[List[BusinessActivity]] = None
    products_sold: Optional[List[ProductSold]] = None

    # A.III Operations
    location_counts: Optional[LocationCounts] = None
    markets_served: Optional[MarketsServed] = None

    # A.IV Employees
    employee_worker_counts: Optional[EmployeeWorkerCounts] = None
    differently_abled_counts: Optional[EmployeeWorkerCounts] = None
    women_participation: Optional[WomenParticipation] = None
    turnover_rates: Optional[List[TurnoverRate]] = None

    # A.V Holding / subsidiary / associate
    group_companies: Optional[List[GroupCompany]] = None

    # A.VI CSR details
    csr_applicable: Optional[bool] = None
    csr_turnover_inr: Optional[Decimal] = Field(default=None, ge=0)
    csr_net_worth_inr: Optional[Decimal] = Field(default=None, ge=0)

    # A.VII Transparency and disclosures
    grievance_redressal: Optional[List[GrievanceEntry]] = None

    # A.VIII Assurance
    assurance_provider_name: Optional[str] = None
    assurance_type: Optional[str] = None


class BrsrOrganizationProfileCreate(BrsrOrganizationProfileBase):
    """All fields optional: BRSR Section A is filled progressively, not in one sitting."""
    pass


class BrsrOrganizationProfileUpdate(BrsrOrganizationProfileBase):
    """Same shape as Create. Only fields present in the request body are applied."""
    pass


class BrsrOrganizationProfileRead(BrsrOrganizationProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
