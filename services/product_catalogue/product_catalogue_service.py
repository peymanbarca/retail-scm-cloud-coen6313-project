from fastapi import FastAPI, Query
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import uuid
import os

app = FastAPI(title="Product Catalogue Service")

mongo_uri = os.getenv("MONGO_URI", "mongodb://user:pass1@localhost:27017/")
client = MongoClient(mongo_uri)
db = client["retail"]

# Load lightweight embedding model from Hugging Face
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


@app.post("/add_product", summary="""
{
  "name": "Wireless Headphones X1",
  "description": "Noise-cancelling over-ear headphones",
  "price": 129.99
}
""")
def add_product(product: dict):
    product_id = str(uuid.uuid4())
    product["id"] = product_id
    product["embedding"] = model.encode(product["description"]).tolist()
    db.products.insert_one(product)
    return {"status": "added", "product_id": product_id}


@app.get("/search")
def search_products(q: str = Query(...)):
    query_vec = model.encode(q).reshape(1, -1)
    products = list(db.products.find({}))
    if not products:
        return {"results": []}

    embeddings = np.array([p["embedding"] for p in products])
    sims = cosine_similarity(query_vec, embeddings)[0]
    ranked = sorted(zip(products, sims), key=lambda x: x[1], reverse=True)

    results = [
        {"id": p["id"], "name": p["name"], "price": p["price"], "similarity": round(s, 3)}
        for p, s in ranked[:5]
    ]
    return {"query": q, "results": results}
