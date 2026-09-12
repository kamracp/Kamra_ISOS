from sqlalchemy.orm import Session, selectinload

from app.models.cbam_good import CbamGood
from app.schemas.cbam_good import CbamGoodCreate, CbamGoodUpdate


class CbamGoodRepository:
    """Tenant-scoped access to cbam_goods. Every query starts from _base_query()."""

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return (self.db.query(CbamGood)
                .options(selectinload(CbamGood.lca_product), selectinload(CbamGood.manufacturing_unit))
                .filter(CbamGood.organization_id == self.organization_id))

    def get_all(self, year: int | None = None) -> list[CbamGood]:
        q = self._base_query()
        if year is not None:
            q = q.filter(CbamGood.reporting_year == year)
        return q.order_by(CbamGood.reporting_year.desc(), CbamGood.name).all()

    def get_by_id(self, good_id: int) -> CbamGood | None:
        return self._base_query().filter(CbamGood.id == good_id).first()

    def create(self, data: CbamGoodCreate) -> CbamGood:
        obj = CbamGood(organization_id=self.organization_id, **data.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: CbamGood, data: CbamGoodUpdate) -> CbamGood:
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: CbamGood) -> None:
        self.db.delete(obj)
        self.db.commit()
