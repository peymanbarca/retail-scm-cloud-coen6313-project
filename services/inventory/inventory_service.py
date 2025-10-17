from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import uuid
from pydantic import BaseModel, Field
from typing import Optional
import os

app = FastAPI(title="Inventory Service")
mongo_uri = os.getenv("MONGO_URI", "mongodb://user:pass1@localhost:27017/")
client = MongoClient(mongo_uri)
db = client["retail"]


# -----------------------------
# Pydantic Schemas
# -----------------------------

class InitStockRequest(BaseModel):
    product_id: str = Field(..., example="5713b251-7b09-47a0-b8ea-ba31cf04a345")
    stock: int = Field(10, ge=0, example=10)


class ReserveRequest(BaseModel):
    product_id: str = Field(..., example="5713b251-7b09-47a0-b8ea-ba31cf04a345")
    qty: int = Field(..., gt=0, example=2)


class ReserveResponse(BaseModel):
    status: str = Field(..., example="reserved")
    reservation_id: Optional[str]


class StockStatusResponse(BaseModel):
    product_id: str
    stock: int


@app.post("/clear_stocks")
def clear_orders():
    """Delete all inventory records (for testing/demo reset)."""
    db.inventory.delete_many({})


@app.post("/init_stock", response_model=StockStatusResponse)
def init_stock(request: InitStockRequest):
    """
    Initialize or reset stock for a product.
    """
    db.inventory.update_one(
        {"product_id": request.product_id},
        {"$set": {"stock": request.stock}},
        upsert=True
    )
    return StockStatusResponse(product_id=request.product_id, stock=request.stock)


@app.post("/reserve", response_model=ReserveResponse)
def reserve(request: ReserveRequest):
    """
    Reserve stock for an order if available, otherwise mark as out of stock.
    Optionally adds artificial delay (for latency testing).
    """
    stock_record = db.inventory.find_one({"product_id": request.product_id})

    if not stock_record:
        return ReserveResponse(status="out_of_stock", reservation_id=None)

    available = stock_record["stock"]

    if available >= request.qty:
        reservation_id = str(uuid.uuid4())
        db.inventory.update_one(
            {"product_id": request.product_id},
            {"$inc": {"stock": -request.qty}},
            upsert=True
        )
        return ReserveResponse(status="reserved", reservation_id=reservation_id)
    else:
        return ReserveResponse(status="out_of_stock", reservation_id=None)


@app.get("/stock/{product_id}", response_model=StockStatusResponse)
def get_stock(product_id: str):
    """
    Retrieve the current stock level for a given product.
    """
    stock_record = db.inventory.find_one({"product_id": product_id})
    if not stock_record:
        raise HTTPException(status_code=404, detail="Item not found")
    return StockStatusResponse(product_id=product_id, stock=stock_record["stock"])
