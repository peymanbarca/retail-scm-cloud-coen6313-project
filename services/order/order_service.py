from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import requests, uuid
import os
from typing import Optional, Literal
from pydantic import BaseModel, Field

app = FastAPI(title="Order Service")
mongo_uri = os.getenv("MONGO_URI", "mongodb://user:pass1@localhost:27017/")
client = MongoClient(mongo_uri)
db = client["retail"]

INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://localhost:8002")


# -----------------------------
# Pydantic Schemas
# -----------------------------

class OrderCreateRequest(BaseModel):
    product_id: str = Field(..., example="5713b251-7b09-47a0-b8ea-ba31cf04a345")
    qty: int = Field(..., gt=0, example=2)


class OrderStatus(str):
    INIT = "INIT"
    RESERVED = "RESERVED"
    COMPLETED = "COMPLETED"
    FAILED_OUT_OF_STOCK = "FAILED_OUT_OF_STOCK"
    FAILED = "FAILED"


class OrderResponse(BaseModel):
    order_id: str
    status: Literal[
        "INIT", "RESERVED", "COMPLETED", "FAILED_OUT_OF_STOCK", "FAILED"
    ]
    reservation_id: Optional[str]


@app.post("/clear_orders")
def clear_orders():
    """Delete all orders (for testing/demo reset)."""
    db.orders.delete_many({})
    return {"message": "All orders cleared"}


@app.post("/order", response_model=OrderResponse)
def create_order(request: OrderCreateRequest):
    """
    Create a new order and attempt to reserve stock from the Inventory Service.
    """

    order_id = str(uuid.uuid4())

    db.orders.insert_one({
        "_id": order_id,
        "product_id": request.product_id,
        "qty": request.qty,
        "status": OrderStatus.INIT
    })

    # Call Inventory Service for reservation
    try:
        response = requests.post(
            f"{INVENTORY_SERVICE_URL}/reserve",
            json={"product_id": request.product_id, "qty": request.qty},
            timeout=10
        )
        res = response.json()
    except Exception as e:
        db.orders.update_one({"_id": order_id}, {"$set": {"status": OrderStatus.FAILED}})
        raise HTTPException(status_code=503, detail=f"Inventory service error: {e}")

    # Process reservation response
    reservation_id = res.get("reservation_id")
    status = res.get("status")

    if status == "reserved":
        db.orders.update_one({"_id": order_id}, {"$set": {"status": OrderStatus.RESERVED}})

        # Call Mock payment --> if success
        db.orders.update_one({"_id": order_id}, {"$set": {"status": OrderStatus.COMPLETED}})

        final_status = OrderStatus.COMPLETED
    elif status == "out_of_stock":
        db.orders.update_one({"_id": order_id}, {"$set": {"status": OrderStatus.FAILED_OUT_OF_STOCK}})
        final_status = OrderStatus.FAILED_OUT_OF_STOCK
    else:
        db.orders.update_one({"_id": order_id}, {"$set": {"status": OrderStatus.FAILED}})
        final_status = OrderStatus.FAILED

    return OrderResponse(
        order_id=order_id,
        status=final_status,
        reservation_id=reservation_id
    )
