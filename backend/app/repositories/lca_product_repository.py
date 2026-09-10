from sqlalchemy.orm import Session, selectinload
from app.models.lca_product import LcaProduct, LcaInventoryItem
from app.schemas.lca_product import (
    LcaProductCreate,
    LcaProductUpdate,
    LcaInventoryItemCreate,
)


class LcaProductRepository:
    """Products and their inventory items, all scoped to one organization."""

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    # ----------------------------------------------------------- products ---

    def _base_query(self):
        return self.db.query(LcaProduct).filter(
            LcaProduct.organization_id == self.organization_id,
        )

    def get_all(self, year: int | None = None) -> list[LcaProduct]:
        query = self._base_query().options(selectinload(LcaProduct.items))
        if year is not None:
            query = query.filter(LcaProduct.reference_year == year)
        return query.order_by(LcaProduct.name.asc()).all()

    def get_by_id(self, product_id: int) -> LcaProduct | None:
        return (
            self._base_query()
            .options(selectinload(LcaProduct.items))
            .filter(LcaProduct.id == product_id)
            .first()
        )

    def create(self, data: LcaProductCreate) -> LcaProduct:
        db_product = LcaProduct(**data.model_dump(), organization_id=self.organization_id)
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def update(self, db_product: LcaProduct, data: LcaProductUpdate) -> LcaProduct:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(db_product, key, value)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def delete(self, db_product: LcaProduct) -> None:
        # Items go with it: ORM cascade delete-orphan + DB ON DELETE CASCADE.
        self.db.delete(db_product)
        self.db.commit()

    # -------------------------------------------------------------- items ---

    def _item_query(self):
        return self.db.query(LcaInventoryItem).filter(
            LcaInventoryItem.organization_id == self.organization_id,
        )

    def get_item(self, product_id: int, item_id: int) -> LcaInventoryItem | None:
        return (
            self._item_query()
            .filter(LcaInventoryItem.product_id == product_id, LcaInventoryItem.id == item_id)
            .first()
        )

    def create_item(self, db_product: LcaProduct, data: LcaInventoryItemCreate) -> LcaInventoryItem:
        db_item = LcaInventoryItem(
            **data.model_dump(),
            product_id=db_product.id,
            organization_id=self.organization_id,
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def update_item(self, db_item: LcaInventoryItem, update_data: dict) -> LcaInventoryItem:
        """update_data is the already-merged, already-validated field dict
        prepared by the service (see LcaProductService.update_item)."""
        for key, value in update_data.items():
            setattr(db_item, key, value)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def delete_item(self, db_item: LcaInventoryItem) -> None:
        self.db.delete(db_item)
        self.db.commit()
