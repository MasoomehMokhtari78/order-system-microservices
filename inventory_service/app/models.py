from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class StockItem(Base):
    __tablename__ = "stock_items"

    id = Column(Integer, primary_key=True, index=True)
    item_sku = Column(String, unique=True, index=True, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    reserved = Column(Integer, nullable=False, default=0)

    reservations = relationship("Reservation", back_populates="item")

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    item_sku = Column(String, ForeignKey("stock_items.item_sku"), nullable=False)
    # how many units of the item are reserved.
    quantity = Column(Integer, nullable=False)
    # active reservation or released/cancelled
    active = Column(Boolean, default=True, nullable=False)

    # links a reservation to the corresponding StockItem object.
    item = relationship("StockItem", primaryjoin="Reservation.item_sku==StockItem.item_sku", uselist=False)
