from sqlalchemy import Column, Integer, Float, String, Boolean
from db import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    authorized = Column(Boolean, nullable=False)
