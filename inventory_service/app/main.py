from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.orm import Session
from db import Base, engine, SessionLocal
from api.v1.endpoints import stock

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables if not exist...")
    Base.metadata.create_all(bind=engine)
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
app.include_router(stock.router)

@app.get("/health")
def health():
    return {"status": "ok"}
