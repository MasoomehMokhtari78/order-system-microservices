from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import SessionLocal
from models import StockItem, Reservation
from schemas.stock import ItemIn, ItemOut, ReserveRequest, ReserveResponse, ReleaseRequest
from typing import List

router = APIRouter(prefix="/api/v1/stock", tags=["stock"])

# create a DB session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# upsert item
@router.post('/items', response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def upsert_item(payload: ItemIn, db: Session = Depends(get_db)):
    sku = payload.item_sku
    item = db.query(StockItem).filter(StockItem.item_sku == sku).first()

    if not item:
        item = StockItem(item_sku=sku, quantity=payload.quantity)
        db.add(item)
        db.commit()
        db.refresh(item) 
        return item

    item.quantity = payload.quantity
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# list all items
@router.get('/', response_model=List[ItemOut])
def list_items(db: Session = Depends(get_db)):
    items = db.query(StockItem).all()
    return items


# get a single item by SKU
@router.get('/{sku}', response_model=ItemOut)
def get_item(sku: str, db: Session = Depends(get_db)):
    item = db.query(StockItem).filter(StockItem.item_sku == sku).first()
    if not item:
        raise HTTPException(status_code=404, detail="item not found")
    return item


# reserve stock
@router.post('/reserve', response_model=ReserveResponse)
def reserve_stock(req: ReserveRequest, db: Session = Depends(get_db)):
    sku = req.item_sku
    qty = req.quantity

    # locking the row
    item = db.query(StockItem).with_for_update().filter(StockItem.item_sku == sku).first()
    if not item:
        raise HTTPException(status_code=404, detail="item not found")

    if item.quantity < qty:
        raise HTTPException(status_code=400, detail="insufficient stock")
    
    # decrease stock
    item.quantity -= qty

    # create a new reservation
    reservation = Reservation(item_sku=sku, quantity=qty, active=True)
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    db.refresh(item)

    return ReserveResponse(
        reservation_id=reservation.id,
        item_sku=sku,
        quantity=qty,
        remaining_quantity=item.quantity
    )


# release reserved item
@router.post("/release", status_code=200)
def release_stock(req: ReleaseRequest, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).with_for_update().filter(Reservation.id == req.reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="reservation not found")
    if not reservation.active:
        raise HTTPException(status_code=400, detail="reservation already released")

    item = db.query(StockItem).with_for_update().filter(StockItem.item_sku == reservation.item_sku).first()
    if not item:
        # mismatch between reservation and stock
        reservation.active = False
        db.add(reservation)
        db.commit()
        raise HTTPException(status_code=500, detail="corrupt inventory state")

    #rollback reserved quantity
    item.quantity += reservation.quantity
    reservation.active = False
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    db.refresh(item)

    return {"released": True, "reservation_id": reservation.id, "item_sku": reservation.item_sku}
