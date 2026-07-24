from app.core.exceptions import ResourceNotFoundException
from app.repositories.decarbonization_project_repository import (
    DecarbonizationProjectRepository,
)
from app.schemas.decarbonization_project import (
    DecarbonizationProjectCreate,
    DecarbonizationProjectResponse,
    DecarbonizationProjectUpdate,
)


class DecarbonizationProjectService:
    def __init__(self, repository: DecarbonizationProjectRepository):
        self.repository = repository

    def get_all(self) -> list[DecarbonizationProjectResponse]:
        return [
            DecarbonizationProjectResponse.model_validate(p)
            for p in self.repository.get_all()
        ]

    def get_by_id(self, project_id: int) -> DecarbonizationProjectResponse:
        project = self.repository.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundException("Decarbonization Project", project_id)
        return DecarbonizationProjectResponse.model_validate(project)

    def create(self, data: DecarbonizationProjectCreate) -> DecarbonizationProjectResponse:
        project = self.repository.create(data)
        return DecarbonizationProjectResponse.model_validate(project)

    def update(
        self, project_id: int, data: DecarbonizationProjectUpdate
    ) -> DecarbonizationProjectResponse:
        project = self.repository.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundException("Decarbonization Project", project_id)
        updated = self.repository.update(project, data)
        return DecarbonizationProjectResponse.model_validate(updated)

    def delete(self, project_id: int) -> None:
        project = self.repository.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundException("Decarbonization Project", project_id)
        self.repository.delete(project)
