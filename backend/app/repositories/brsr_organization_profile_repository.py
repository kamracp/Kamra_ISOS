from sqlalchemy.orm import Session

from app.models.brsr_organization_profile import BrsrOrganizationProfile
from app.schemas.brsr_organization_profile import (
    BrsrOrganizationProfileCreate,
    BrsrOrganizationProfileUpdate,
)


class BrsrOrganizationProfileRepository:
    """
    Data access for BRSR Section A profiles.

    Tenant-scoped at construction time, matching the project convention:
    the organization filter lives in _base_query() only, so no method can
    accidentally read across tenants.

    This table is 1:1 with Organization, so there is no get_all(): an
    organization has exactly zero or one profile.
    """

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return self.db.query(BrsrOrganizationProfile).filter(
            BrsrOrganizationProfile.organization_id == self.organization_id,
        )

    def get(self) -> BrsrOrganizationProfile | None:
        return self._base_query().first()

    def create(
        self, data: BrsrOrganizationProfileCreate
    ) -> BrsrOrganizationProfile:
        # mode="json" converts nested Pydantic models (LocationCounts, etc.)
        # and Decimal values into plain JSON-safe types for the JSONB columns.
        payload = data.model_dump(exclude_unset=True, mode="json")
        db_profile = BrsrOrganizationProfile(
            **payload, organization_id=self.organization_id
        )
        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def update(
        self,
        db_profile: BrsrOrganizationProfile,
        data: BrsrOrganizationProfileUpdate,
    ) -> BrsrOrganizationProfile:
        # exclude_unset=True is critical: only fields actually present in the
        # request body are applied. Without it, a partial update would null
        # out every field the client did not send.
        payload = data.model_dump(exclude_unset=True, mode="json")
        for field, value in payload.items():
            setattr(db_profile, field, value)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def upsert(
        self, data: BrsrOrganizationProfileUpdate
    ) -> BrsrOrganizationProfile:
        """
        Create the profile if absent, otherwise update it.

        BRSR Section A is filled progressively across many sessions, so the
        client should not have to know whether a profile row exists yet.
        """
        existing = self.get()
        if existing is None:
            return self.create(
                BrsrOrganizationProfileCreate(
                    **data.model_dump(exclude_unset=True)
                )
            )
        return self.update(existing, data)

    def delete(self, db_profile: BrsrOrganizationProfile) -> None:
        self.db.delete(db_profile)
        self.db.commit()
