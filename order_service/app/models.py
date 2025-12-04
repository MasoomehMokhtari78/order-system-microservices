from sqlalchemy import Column, Integer, String, Float
from db import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    item_sku = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    payment_status = Column(String, default="PENDING")
    idempotency_key = Column(String, unique=True, nullable=False)
