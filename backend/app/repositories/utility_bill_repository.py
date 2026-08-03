from datetime import date

from sqlalchemy.orm import Session

from app.models.utility_bill import UtilityBill
from app.schemas.utility_bill import UtilityBillCreate, UtilityBillUpdate


class UtilityBillRepository:
    """All queries are scoped to a single organization (tenant)."""

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return self.db.query(UtilityBill).filter(
            UtilityBill.organization_id == self.organization_id,
        )

    def get_all(
        self,
        meter_id: int | None = None,
        year: int | None = None,
    ) -> list[UtilityBill]:
        """Return bills, optionally scoped to one meter and/or one
        calendar year (matched against billing_period_start, the same
        field already used for factor lookup — see CarbonService).
        """
        query = self._base_query()

        if meter_id is not None:
            query = query.filter(UtilityBill.meter_id == meter_id)

        if year is not None:
            query = query.filter(
                UtilityBill.billing_period_start >= date(year, 1, 1),
                UtilityBill.billing_period_start <= date(year, 12, 31),
            )

        return (
            query
            .order_by(UtilityBill.billing_period_start.desc())
            .all()
        )

    def get_by_id(self, bill_id: int) -> UtilityBill | None:
        return (
            self._base_query()
            .filter(UtilityBill.id == bill_id)
            .first()
        )

    def find_overlapping(
        self,
        meter_id: int,
        period_start: date,
        period_end: date,
        exclude_bill_id: int | None = None,
    ) -> UtilityBill | None:
        """Return a bill on the same meter whose period overlaps
        [period_start, period_end], if any.

        Overlapping periods would double-count consumption in
        emission calculations, so they are forbidden.
        """
        query = self._base_query().filter(
            UtilityBill.meter_id == meter_id,
            UtilityBill.billing_period_start <= period_end,
            UtilityBill.billing_period_end >= period_start,
        )

        if exclude_bill_id is not None:
            query = query.filter(UtilityBill.id != exclude_bill_id)

        return query.first()

    def create(self, bill: UtilityBillCreate) -> UtilityBill:
        db_bill = UtilityBill(
            **bill.model_dump(),
            organization_id=self.organization_id,
        )

        self.db.add(db_bill)
        self.db.commit()
        self.db.refresh(db_bill)

        return db_bill

    def update(
        self,
        db_bill: UtilityBill,
        bill: UtilityBillUpdate,
    ) -> UtilityBill:
        update_data = bill.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_bill, key, value)

        self.db.commit()
        self.db.refresh(db_bill)

        return db_bill

    def delete(self, db_bill: UtilityBill) -> None:
        self.db.delete(db_bill)
        self.db.commit()