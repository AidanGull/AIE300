from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# In-memory "database"
items_db = {}
current_id = 1

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------- API ROUTES -----------

@app.get("/items")
def get_items():
    return [{"id": id, **data} for id, data in items_db.items()]


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, **items_db[item_id]}


@app.post("/items")
def create_item(item: dict):
    global current_id
    items_db[current_id] = item
    response = {"id": current_id, **item}
    current_id += 1
    return response


@app.put("/items/{item_id}")
def update_item(item_id: int, item: dict):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[item_id] = item
    return {"id": item_id, **item}


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    return {"message": "Item deleted"}


# ----------- STATIC FRONTEND -----------

# MUST be at the bottom (after routes)
app.mount("/", StaticFiles(directory="static", html=True), name="static")