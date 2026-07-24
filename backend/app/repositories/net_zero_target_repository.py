from sqlalchemy.orm import Session

from app.models.net_zero_target import NetZeroTarget
from app.schemas.net_zero_target import NetZeroTargetCreate, NetZeroTargetUpdate


class NetZeroTargetRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return self.db.query(NetZeroTarget).filter(
            NetZeroTarget.organization_id == self.organization_id,
        )

    def get_all(self) -> list[NetZeroTarget]:
        return self._base_query().order_by(NetZeroTarget.target_year.asc()).all()

    def get_by_id(self, target_id: int) -> NetZeroTarget | None:
        return self._base_query().filter(NetZeroTarget.id == target_id).first()

    def create(self, data: NetZeroTargetCreate) -> NetZeroTarget:
        db_target = NetZeroTarget(**data.model_dump(), organization_id=self.organization_id)
        self.db.add(db_target)
        self.db.commit()
        self.db.refresh(db_target)
        return db_target

    def update(self, db_target: NetZeroTarget, data: NetZeroTargetUpdate) -> NetZeroTarget:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_target, key, value)
        self.db.commit()
        self.db.refresh(db_target)
        return db_target

    def delete(self, db_target: NetZeroTarget) -> None:
        self.db.delete(db_target)
        self.db.commit()
