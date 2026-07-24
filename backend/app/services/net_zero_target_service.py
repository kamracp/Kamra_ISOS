from app.core.exceptions import ResourceNotFoundException
from app.repositories.net_zero_target_repository import NetZeroTargetRepository
from app.schemas.net_zero_target import (
    NetZeroTargetCreate,
    NetZeroTargetResponse,
    NetZeroTargetUpdate,
)


class NetZeroTargetService:
    def __init__(self, repository: NetZeroTargetRepository):
        self.repository = repository

    def get_all(self) -> list[NetZeroTargetResponse]:
        return [NetZeroTargetResponse.model_validate(t) for t in self.repository.get_all()]

    def get_by_id(self, target_id: int) -> NetZeroTargetResponse:
        target = self.repository.get_by_id(target_id)
        if not target:
            raise ResourceNotFoundException("Net Zero Target", target_id)
        return NetZeroTargetResponse.model_validate(target)

    def create(self, data: NetZeroTargetCreate) -> NetZeroTargetResponse:
        target = self.repository.create(data)
        return NetZeroTargetResponse.model_validate(target)

    def update(self, target_id: int, data: NetZeroTargetUpdate) -> NetZeroTargetResponse:
        target = self.repository.get_by_id(target_id)
        if not target:
            raise ResourceNotFoundException("Net Zero Target", target_id)
        updated = self.repository.update(target, data)
        return NetZeroTargetResponse.model_validate(updated)

    def delete(self, target_id: int) -> None:
        target = self.repository.get_by_id(target_id)
        if not target:
            raise ResourceNotFoundException("Net Zero Target", target_id)
        self.repository.delete(target)
