from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi.staticfiles import StaticFiles
# -----------------------
# Database setup (SQLite)
# -----------------------
DATABASE_URL = "sqlite:///./data/items.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# -----------------------
# Database model
# -----------------------
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)


# Create tables automatically
Base.metadata.create_all(bind=engine)


# -----------------------
# Pydantic models
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


# -----------------------
# FastAPI app
# -----------------------
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------
# Routes
# -----------------------

# Get all items
@app.get("/items", response_model=list[ItemRead])
def get_items():
    db = SessionLocal()
    items = db.query(Item).all()
    db.close()
    return items


# Get single item
@app.get("/items/{item_id}", response_model=ItemRead)
def get_item(item_id: int):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    db.close()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


# Create item
@app.post("/items", response_model=ItemRead, status_code=201)
def create_item(item: ItemCreate):
    db = SessionLocal()

    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    db.close()
    return db_item


# Update item
@app.put("/items/{item_id}", response_model=ItemRead)
def update_item(item_id: int, updated: ItemCreate):
    db = SessionLocal()

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    item.name = updated.name
    item.description = updated.description

    db.commit()
    db.refresh(item)
    db.close()

    return item


# Delete item
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    db = SessionLocal()

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    db.close()

    return {"message": "Item deleted"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")