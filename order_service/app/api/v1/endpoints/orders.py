from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Order
from schemas.order import OrderIn, OrderOut
import requests
from typing import List

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

INVENTORY_URL = "http://inventory_service:8000/api/v1/stock"
PAYMENT_URL = "http://payment_service:8000/api/v1/payments"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# create order
@router.post("/", response_model=OrderOut)
def create_order(order: OrderIn, db: Session = Depends(get_db)):
    # check idempotency
    existing_order = db.query(Order).filter(Order.idempotency_key == order.idempotency_key).first()
    if existing_order:
        return existing_order

    # reserve stock
    resp = requests.post(f"{INVENTORY_URL}/reserve", json={"item_sku": order.item_sku, "quantity": order.quantity})
    if resp.status_code != 200:
        detail = resp.json().get("detail", "Stock reservation failed")
        raise HTTPException(status_code=resp.status_code, detail=detail)

    reservation_id = resp.json()["reservation_id"]

    # process payment
    payment_resp = requests.post(f"{PAYMENT_URL}/authorize", json={
        "order_id": reservation_id,
        "amount": order.amount,
        "currency": order.currency
    })

    order_status = "CONFIRMED"
    payment_status = "SUCCEEDED"

    if payment_resp.status_code != 200 or not payment_resp.json().get("authorized", False):
        # release stock if payment fails
        release_resp = requests.post(f"{INVENTORY_URL}/release", json={"reservation_id": reservation_id})
    
        order_status = "FAILED"
        payment_status = "FAILED"

        
        # log release info
        if release_resp.status_code == 200:
            print(f"Stock released: {release_resp.json()}")

    # save order
    db_order = Order(
        item_sku=order.item_sku,
        quantity=order.quantity,
        amount=order.amount,
        currency=order.currency,
        status=order_status,
        payment_status=payment_status,
        idempotency_key=order.idempotency_key
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

# list orders
@router.get("/", response_model=List[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

# get order by ID
@router.get("/{id}", response_model=OrderOut)
def get_order(id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
