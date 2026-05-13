from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

import requests

DATABASE_URL = "sqlite:///./data/items.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)


Base.metadata.create_all(bind=engine)


class ItemCreate(BaseModel):
    name: str
    description: str | None = None


class ItemRead(BaseModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class PredictionRequest(BaseModel):
    features: list[float]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/items", response_model=list[ItemRead])
def get_items():

    db = SessionLocal()

    items = db.query(ItemDB).all()

    db.close()

    return items


@app.post(
    "/items",
    response_model=ItemRead,
    status_code=status.HTTP_201_CREATED
)
def create_item(item: ItemCreate):

    db = SessionLocal()

    db_item = ItemDB(
        name=item.name,
        description=item.description
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    db.close()

    return db_item


@app.delete("/items/{item_id}")
def delete_item(item_id: int):

    db = SessionLocal()

    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()

    if not item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()

    db.close()

    return {"message": "Item deleted"}


@app.post("/predict")
def predict(data: PredictionRequest):

    response = requests.post(
        "http://model-service:8001/predict",
        json={"features": data.features}
    )

    return response.json()


app.mount("/", StaticFiles(directory="static", html=True), name="static")
