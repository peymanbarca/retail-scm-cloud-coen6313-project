from fastapi import FastAPI, Query, HTTPException
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import numpy as np
from pydantic import BaseModel, Field
from typing import List, Optional
from sklearn.metrics.pairwise import cosine_similarity
import uuid
import os

app = FastAPI(title="Product Catalogue Service", version="1.0")

mongo_uri = os.getenv("MONGO_URI", "mongodb://user:pass1@localhost:27017/")
client = MongoClient(mongo_uri)
db = client["retail"]

# Load lightweight embedding model from Hugging Face
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


# -----------------------------
# Pydantic Schemas
# -----------------------------
class ProductIn(BaseModel):
    name: str = Field(..., example="Wireless Headphones X1")
    description: str = Field(..., example="Noise-cancelling over-ear headphones with 30h battery life")
    price: float = Field(..., gt=0, example=129.99)


class ProductOut(BaseModel):
    id: str
    name: str
    description: str
    price: float


class ProductSearchResultItem(ProductOut):
    similarity: float


class ProductSearchResponse(BaseModel):
    query: str
    results: List[ProductSearchResultItem]


class StatusResponse(BaseModel):
    status: str
    product_id: str


@app.post("/add_product", response_model=StatusResponse, summary="Add a new product to the catalog")
def add_product(product: ProductIn):
    """
    Add a new product to the catalog, generate its embedding, and store it in MongoDB.
    """
    existing_product = db.products.find_one({"name": product.name})
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with the same name existed.")

    product_id = str(uuid.uuid4())
    embedding = model.encode(product.description).tolist()

    doc = {
        "_id": product_id,
        "id": product_id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "embedding": embedding
    }

    db.products.insert_one(doc)
    return StatusResponse(status="added", product_id=product_id)


@app.get("/products", response_model=List[ProductOut])
def get_all_products():
    """
    Retrieve all products from the catalog.
    """
    products = list(db.products.find({}, {"_id": 0, "embedding": 0}))
    return [ProductOut(**p) for p in products]


@app.get("/search", response_model=ProductSearchResponse)
def search_products(q: str = Query(..., example="noise cancelling headphones")):
    """
    Search for products semantically similar to the query using embedding cosine similarity.
    """
    products = list(db.products.find({}))
    if not products:
        return ProductSearchResponse(query=q, results=[])

    query_vec = model.encode(q).reshape(1, -1)
    embeddings = np.array([p["embedding"] for p in products])
    sims = cosine_similarity(query_vec, embeddings)[0]

    ranked = sorted(zip(products, sims), key=lambda x: x[1], reverse=True)
    results = [
        ProductSearchResultItem(
            id=p["id"],
            name=p["name"],
            description=p["description"],
            price=p["price"],
            similarity=round(float(s), 3)
        )
        for p, s in ranked[:5]
    ]
    return ProductSearchResponse(query=q, results=results)
