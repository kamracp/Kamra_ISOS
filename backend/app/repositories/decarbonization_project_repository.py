from sqlalchemy.orm import Session

from app.models.decarbonization_project import DecarbonizationProject
from app.schemas.decarbonization_project import (
    DecarbonizationProjectCreate,
    DecarbonizationProjectUpdate,
)


class DecarbonizationProjectRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return self.db.query(DecarbonizationProject).filter(
            DecarbonizationProject.organization_id == self.organization_id,
        )

    def get_all(self) -> list[DecarbonizationProject]:
        return self._base_query().order_by(DecarbonizationProject.project_name.asc()).all()

    def get_by_id(self, project_id: int) -> DecarbonizationProject | None:
        return self._base_query().filter(DecarbonizationProject.id == project_id).first()

    def create(self, data: DecarbonizationProjectCreate) -> DecarbonizationProject:
        db_project = DecarbonizationProject(
            **data.model_dump(), organization_id=self.organization_id
        )
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def update(
        self, db_project: DecarbonizationProject, data: DecarbonizationProjectUpdate
    ) -> DecarbonizationProject:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def delete(self, db_project: DecarbonizationProject) -> None:
        self.db.delete(db_project)
        self.db.commit()
