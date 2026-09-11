"""
LCA/PCF Studio API.

Products:
  GET    /lca-products/              list (with headline GWP, no items)
  POST   /lca-products/              create
  GET    /lca-products/{id}          full product + items + by_stage GWP breakdown
  PUT    /lca-products/{id}          update
  DELETE /lca-products/{id}

Items (nested under a product):
  POST   /lca-products/{id}/items            add inventory item
  PUT    /lca-products/{id}/items/{item_id}  update item
  DELETE /lca-products/{id}/items/{item_id}

Every mutating response returns the full product (with recalculated GWP)
so the frontend never needs a separate refetch.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.lca_product import (
    LcaProductCreate,
    LcaProductUpdate,
    LcaInventoryItemCreate,
    LcaInventoryItemUpdate,
)
from app.services.lca_product_service import LcaProductService
from app.services.lca_openlca_export import build_openlca_zip

router = APIRouter(prefix="/lca-products", tags=["LCA / PCF Studio"])


def get_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LcaProductService:
    return LcaProductService(db, organization_id=current_user.organization_id)


def _404(product_id: int):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"LCA product {product_id} not found")


# ------------------------------------------------------------ products ---

@router.get("/")
def list_products(
    year: int | None = None,
    service: LcaProductService = Depends(get_service),
):
    return service.list_products(year)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(
    data: LcaProductCreate,
    service: LcaProductService = Depends(get_service),
):
    return service.create_product(data)


@router.get("/{product_id}")
def get_product(
    product_id: int,
    service: LcaProductService = Depends(get_service),
):
    result = service.get_product(product_id)
    if result is None:
        _404(product_id)
    return result


@router.put("/{product_id}")
def update_product(
    product_id: int,
    data: LcaProductUpdate,
    service: LcaProductService = Depends(get_service),
):
    result = service.update_product(product_id, data)
    if result is None:
        _404(product_id)
    return result


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    service: LcaProductService = Depends(get_service),
):
    if not service.delete_product(product_id):
        _404(product_id)


# --------------------------------------------------------------- items ---

@router.post("/{product_id}/items", status_code=status.HTTP_201_CREATED)
def add_item(
    product_id: int,
    data: LcaInventoryItemCreate,
    service: LcaProductService = Depends(get_service),
):
    result = service.add_item(product_id, data)
    if result is None:
        _404(product_id)
    return result


@router.put("/{product_id}/items/{item_id}")
def update_item(
    product_id: int,
    item_id: int,
    data: LcaInventoryItemUpdate,
    service: LcaProductService = Depends(get_service),
):
    try:
        result = service.update_item(product_id, item_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Item {item_id} not found in product {product_id}")
    return result


@router.delete("/{product_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    product_id: int,
    item_id: int,
    service: LcaProductService = Depends(get_service),
):
    result = service.delete_item(product_id, item_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Item {item_id} not found in product {product_id}")


# ------------------------------------------------------------- export ---

@router.get("/{product_id}/export/openlca")
def export_openlca(product_id: int, svc: LcaProductService = Depends(get_service)):
    """openLCA JSON-LD zip (olca-schema v2): process + flows + Kamra GWP method
    carrying the exact resolved factors, so the result can be reproduced in openLCA."""
    product = svc.get_product(product_id)
    if product is None:
        _404(product_id)
    data = build_openlca_zip(product)
    filename = f"kamra_lca_product_{product_id}_openlca.zip"
    return Response(content=data, media_type="application/zip",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})
