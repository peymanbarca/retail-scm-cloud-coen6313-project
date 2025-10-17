from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
import requests
import os

app = FastAPI(title="API Gateway")

CATALOGUE_URL = os.getenv("CATALOGUE_URL", "http://localhost:8004")
ORDER_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:8001")
PAYMENT_URL = os.getenv("PAYMENT_URL", "http://localhost:8003")


# -----------------------------
# Pydantic Schemas
# -----------------------------
class PurchaseRequest(BaseModel):
    product_id: str = Field(..., example="5713b251-7b09-47a0-b8ea-ba31cf04a345")
    qty: int = Field(..., gt=0, example=2)


class PurchaseResponse(BaseModel):
    order_id: str
    status: Literal["INIT", "RESERVED", "COMPLETED", "FAILED", "FAILED_OUT_OF_STOCK"]


@app.get("/search")
def search_products(q: str):
    r = requests.get(f"{CATALOGUE_URL}/search", params={"q": q})
    return r.json()


@app.post("/purchase", response_model=PurchaseResponse, summary="Initiate purchase for a product")
def purchase_cart(request: PurchaseRequest):
    """
    Orchestrates the purchase workflow:
    1. Calls Order Service to create an order.
    2. Waits for its final status (order + inventory + payment handled downstream).
    """
    try:
        resp = requests.post(
            f"{ORDER_URL}/order",
            json={"product_id": request.product_id, "qty": request.qty},
            timeout=10
        )

        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"Order service error: {resp.text}")

        data = resp.json()
        return PurchaseResponse(
            order_id=data["order_id"],
            status=data["status"]
        )

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Failed to reach Order Service: {e}")
