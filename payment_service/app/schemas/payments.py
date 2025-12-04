from pydantic import BaseModel

class PaymentRequest(BaseModel):
    order_id: int
    amount: float
    currency: str

class PaymentResponse(BaseModel):
    payment_id: int
    authorized: bool
