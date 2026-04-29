from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import torch
import torch.nn as nn
import os

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base


# -----------------------
# DATABASE
# -----------------------
DATABASE_URL = "sqlite:///./data/items.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)


Base.metadata.create_all(bind=engine)


# -----------------------
# PYDANTIC MODELS
# -----------------------
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


# -----------------------
# PYTORCH MODEL
# -----------------------
class SimpleClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(4, 16)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(16, 3)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        return self.fc2(x)


# 🔥 FIXED MODEL PATH (works in Docker)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model.pth")

model = SimpleClassifier()
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cpu")))
model.eval()

labels = ["setosa", "versicolor", "virginica"]


# -----------------------
# FASTAPI
# -----------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------
# CRUD ROUTES
# -----------------------
@app.get("/items", response_model=list[ItemRead])
def get_items():
    db = SessionLocal()
    items = db.query(ItemDB).all()
    db.close()
    return items


@app.get("/items/{item_id}", response_model=ItemRead)
def get_item(item_id: int):
    db = SessionLocal()
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    db.close()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@app.post("/items", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    db = SessionLocal()

    db_item = ItemDB(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    db.close()
    return db_item


@app.put("/items/{item_id}", response_model=ItemRead)
def update_item(item_id: int, updated: ItemCreate):
    db = SessionLocal()

    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if not item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    item.name = updated.name
    item.description = updated.description

    db.commit()
    db.refresh(item)
    db.close()

    return item


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


# -----------------------
# PREDICT ENDPOINT
# -----------------------
@app.post("/predict")
def predict(req: PredictionRequest):
    x = torch.tensor([req.features], dtype=torch.float32)

    with torch.no_grad():
        outputs = model(x)
        probs = torch.softmax(outputs, dim=1)
        pred = torch.argmax(probs, dim=1).item()
        confidence = probs[0][pred].item()

    return {
        "prediction": labels[pred],
        "confidence": round(confidence, 3)
    }
from pydantic import BaseModel
import torch

class PredictionRequest(BaseModel):
    features: list[float]

@app.post("/predict")
def predict(req: PredictionRequest):
    x = torch.tensor([req.features], dtype=torch.float32)

    with torch.no_grad():
        outputs = model(x)
        probs = torch.softmax(outputs, dim=1)
        pred = torch.argmax(probs, dim=1).item()

    return {
        "prediction": int(pred)
    }

# -----------------------
# SERVE FRONTEND
# -----------------------
app.mount("/", StaticFiles(directory="static", html=True), name="static")