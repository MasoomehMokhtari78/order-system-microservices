from fastapi import FastAPI
from api.v1.endpoints import payments
from db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Payment Service")

app.include_router(payments.router)

@app.get("/health")
def health():
    return {"status": "ok"}
