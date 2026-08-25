"""
ESG Report API.

GET /esg-reports/brsr-principle6?year=YYYY
GET /esg-reports/brsr-principle6/pdf?year=YYYY
GET /esg-reports/gri-305?year=YYYY
GET /esg-reports/gri-305/pdf?year=YYYY
GET /esg-reports/esrs-e1?year=YYYY
GET /esg-reports/esrs-e1/pdf?year=YYYY
GET /esg-reports/emission-factor-sources

Returns structured (or PDF) reports for the current user's
organization, built from existing platform data.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.repositories.emission_factor_repository import EmissionFactorRepository
from app.services.esg_report_service import generate_brsr_principle1, generate_brsr_principle6, generate_brsr_principle8, generate_gri_305, generate_esrs_e1, generate_trend
from app.services.esg_report_pdf import generate_brsr_principle6_pdf

router = APIRouter(prefix="/esg-reports", tags=["ESG Reports"])


@router.get("/brsr-principle1")
def brsr_principle1(
    year: int = 2024,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """BRSR Principle 1 (Ethics, Transparency & Accountability) report for the caller's organization."""
    return generate_brsr_principle1(
        db=db,
        organization_id=current_user.organization_id,
        reporting_year=year,
    )


@router.get("/brsr-principle6")
def brsr_principle6(
    year: int = 2024,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """BRSR Principle 6 (Environment) report for the caller's organization."""
    return generate_brsr_principle6(
        db=db,
        organization_id=current_user.organization_id,
        reporting_year=year,
    )


@router.get("/brsr-principle6/pdf")
def brsr_principle6_pdf(
    year: int = 2024,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """BRSR Principle 6 report as a downloadable PDF."""
    report = generate_brsr_principle6(
        db=db,
        organization_id=current_user.organization_id,
        reporting_year=year,
    )
    pdf_bytes = generate_brsr_principle6_pdf(report)

    filename = f"brsr-principle6-org{current_user.organization_id}-{year}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/brsr-principle8")
def brsr_principle8(
    year: int = 2024,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """BRSR Principle 8 (CSR) report for the caller's organization."""
    return generate_brsr_principle8(
        db=db,
        organization_id=current_user.organization_id,
        reporting_year=year,
    )


@router.get("/gri-305")
def gri_305(
    year: int = 2024,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GRI 305 (Emissions) report for the caller's organization."""
    return generate_gri_305(
        db=db,
        organization_id=current_user.organization_id,
        reporting_year=year,
    )


@router.get("/gri-305/pdf")
def gri_305_pdf(
    year: int = 2024,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GRI 305 report as a downloadable PDF."""
    report = generate_gri_305(
        db=db,
        organization_id=current_user.organization_id,
        reporting_year=year,
    )
    pdf_bytes = generate_brsr_principle6_pdf(report)

    filename = f"gri-305-org{current_user.organization_id}-{year}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/esrs-e1")
def esrs_e1(
    year: int = 2024,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """ESRS E1 (Climate Change / CSRD) report for the caller's organization."""
    return generate_esrs_e1(
        db=db,
        organization_id=current_user.organization_id,
        reporting_year=year,
    )


@router.get("/esrs-e1/pdf")
def esrs_e1_pdf(
    year: int = 2024,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """ESRS E1 report as a downloadable PDF."""
    report = generate_esrs_e1(
        db=db,
        organization_id=current_user.organization_id,
        reporting_year=year,
    )
    pdf_bytes = generate_brsr_principle6_pdf(report)

    filename = f"esrs-e1-org{current_user.organization_id}-{year}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/emission-factor-sources")
def emission_factor_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Transparency appendix: every active emission factor the platform
    uses, with its exact official source, publication year, document
    reference, and validity window. Global reference data -- not
    tenant-scoped, since these are the same published facts (CEA,
    DEFRA, IPCC, Ember, TGO...) for every organization.
    """
    repository = EmissionFactorRepository(db)
    factors = repository.get_all()

    return [
        {
            "meter_type": factor.meter_type,
            "unit": factor.unit,
            "region": factor.region,
            "factor_kgco2e_per_unit": factor.factor_kgco2e_per_unit,
            "source": factor.source,
            "source_year": factor.source_year,
            "document_reference": factor.document_reference,
            "valid_from": factor.valid_from.isoformat(),
            "valid_to": factor.valid_to.isoformat() if factor.valid_to else None,
            "notes": factor.notes,
        }
        for factor in factors
    ]


@router.get("/trend")
def esg_trend(
    years: str = "2022,2023,2024",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Multi-year emissions trend table. Pass years as comma-separated: ?years=2022,2023,2024"""
    year_list = [int(y.strip()) for y in years.split(",")]
    return generate_trend(
        db=db,
        organization_id=current_user.organization_id,
        years=year_list,
    )

