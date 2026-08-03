"""
ESG Report API.

GET /esg-reports/brsr-principle6?year=YYYY
GET /esg-reports/brsr-principle6/pdf?year=YYYY
GET /esg-reports/gri-305?year=YYYY
GET /esg-reports/gri-305/pdf?year=YYYY

Returns structured (or PDF) reports for the current user's
organization, built from existing platform data.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.services.esg_report_service import generate_brsr_principle6, generate_gri_305
from app.services.esg_report_pdf import generate_brsr_principle6_pdf

router = APIRouter(prefix="/esg-reports", tags=["ESG Reports"])


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