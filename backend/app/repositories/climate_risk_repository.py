from sqlalchemy.orm import Session

from app.models.climate_risk import ClimateRisk
from app.schemas.climate_risk import ClimateRiskCreate, ClimateRiskUpdate


class ClimateRiskRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return self.db.query(ClimateRisk).filter(
            ClimateRisk.organization_id == self.organization_id,
        )

    def get_all(self) -> list[ClimateRisk]:
        return self._base_query().order_by(ClimateRisk.risk_name.asc()).all()

    def get_by_id(self, risk_id: int) -> ClimateRisk | None:
        return self._base_query().filter(ClimateRisk.id == risk_id).first()

    def create(self, data: ClimateRiskCreate) -> ClimateRisk:
        db_risk = ClimateRisk(
            **data.model_dump(), organization_id=self.organization_id
        )
        self.db.add(db_risk)
        self.db.commit()
        self.db.refresh(db_risk)
        return db_risk

    def update(self, db_risk: ClimateRisk, data: ClimateRiskUpdate) -> ClimateRisk:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_risk, key, value)
        self.db.commit()
        self.db.refresh(db_risk)
        return db_risk

    def delete(self, db_risk: ClimateRisk) -> None:
        self.db.delete(db_risk)
        self.db.commit()
