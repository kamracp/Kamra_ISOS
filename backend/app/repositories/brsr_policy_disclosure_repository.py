from sqlalchemy.orm import Session

from app.models.brsr_policy_disclosure import BrsrPolicyDisclosure
from app.schemas.brsr_policy_disclosure import BrsrPolicyDisclosureUpdate


class BrsrPolicyDisclosureRepository:
    """
    Data access for BRSR Section B policy disclosures.

    Tenant-scoped at construction, with the organization filter living in
    _base_query() only, per project convention.
    """

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return self.db.query(BrsrPolicyDisclosure).filter(
            BrsrPolicyDisclosure.organization_id == self.organization_id,
        )

    def get_all(self) -> list[BrsrPolicyDisclosure]:
        return self._base_query().order_by(BrsrPolicyDisclosure.principle.asc()).all()

    def get_by_principle(self, principle: int) -> BrsrPolicyDisclosure | None:
        return self._base_query().filter(
            BrsrPolicyDisclosure.principle == principle
        ).first()

    def bulk_upsert(
        self, disclosures: list[BrsrPolicyDisclosureUpdate]
    ) -> list[BrsrPolicyDisclosure]:
        """
        Create or update several principles in one transaction.

        Existing rows are fetched once and indexed by principle rather than
        queried per item, and the commit happens once at the end - so a
        nine-principle save either lands whole or not at all.
        """
        existing = {row.principle: row for row in self.get_all()}

        for item in disclosures:
            payload = item.model_dump(exclude_unset=True, exclude={"principle"})
            row = existing.get(item.principle)
            if row is None:
                row = BrsrPolicyDisclosure(
                    organization_id=self.organization_id,
                    principle=item.principle,
                    **payload,
                )
                self.db.add(row)
                existing[item.principle] = row
            else:
                for field, value in payload.items():
                    setattr(row, field, value)

        self.db.commit()
        return self.get_all()

    def delete_all(self) -> int:
        count = self._base_query().delete()
        self.db.commit()
        return count
