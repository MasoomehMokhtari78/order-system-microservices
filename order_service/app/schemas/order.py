from pydantic import BaseModel

class OrderIn(BaseModel):
    item_sku: str
    quantity: int
    amount: float
    currency: str
    idempotency_key: str

class OrderOut(BaseModel):
    id: int
    item_sku: str
    quantity: int
    amount: float
    currency: str
    status: str
    payment_status: str

    class Config:
        orm_mode = True
