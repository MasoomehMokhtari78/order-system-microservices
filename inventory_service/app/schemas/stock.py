from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated

ItemSKU = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

# input model for creating/updating stock
class ItemIn(BaseModel):
    item_sku: ItemSKU
    quantity: int = Field(..., ge=0)

# output model for returning stock details
class ItemOut(BaseModel):
    item_sku: str
    quantity: int
    reserved: int

    # class Config:
        # orm_mode = True

# request model for reserving inventory
class ReserveRequest(BaseModel):
    item_sku: ItemSKU
    quantity: int = Field(..., gt=0)

# response after successful reservation
class ReserveResponse(BaseModel):
    reservation_id: int
    item_sku: str
    quantity: int
    remaining_quantity: int

# request to release a reservation
class ReleaseRequest(BaseModel):
    reservation_id: int