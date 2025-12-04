from fastapi import FastAPI
from db import Base, engine
from api.v1.endpoints import orders

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(orders.router)

@app.get("/health")
def health():
    return {"status": "ok"}
