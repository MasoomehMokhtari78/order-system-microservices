from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Payment
from schemas.payments import PaymentRequest, PaymentResponse

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/authorize", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
def authorize_payment(req: PaymentRequest, db: Session = Depends(get_db)):
    # <1000 = authorized, >=1000 = rejected
    authorized = req.amount < 1000

    payment = Payment(
        order_id=req.order_id,
        amount=req.amount,
        currency=req.currency,
        authorized=authorized
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return PaymentResponse(payment_id=payment.id, authorized=authorized)
