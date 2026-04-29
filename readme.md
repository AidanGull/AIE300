# FastAPI Item Manager

A simple REST API built with FastAPI that allows you to create, read, update, and delete items using in-memory storage.

---

##  Installation

1. Clone the repository:

```bash
git clone https://github.com/AidanGull/AIE300.git
cd AIE300
```

2. (Optional but recommended) Create and activate a virtual environment:

**Windows**

```bash
venv\Scripts\activate
```

**Mac/Linux**

```bash
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Server

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

Then open your browser:

* API: http://localhost:8000
* Docs (Swagger UI): http://localhost:8000/docs

---

## 📌 Available Endpoints

### GET /items

* Returns a list of all items
* Status: `200 OK`

---

### GET /items/{id}

* Returns a single item by ID
* Status: `200 OK` or `404 Not Found`

---

### POST /items

* Creates a new item from JSON body
* Status: `201 Created`

**Example body:**

```json
{
  "name": "Laptop",
  "description": "Gaming laptop"
}
```

---

### PUT /items/{id}

* Updates an existing item
* Status: `200 OK` or `404 Not Found`

---

### DELETE /items/{id}

* Deletes an item by ID
* Status: `200 OK` or `404 Not Found`

---
# AIE300 Full Stack App

## Run with Docker
```bash
docker-compose up --build

## 🧠 Notes

* Data is stored in-memory and will reset when the server restarts.
* IDs are auto-incremented for each new item.

