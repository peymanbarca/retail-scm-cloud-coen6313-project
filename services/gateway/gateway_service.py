from fastapi import FastAPI
import requests

app = FastAPI(title="API Gateway")

CATALOGUE_URL = "http://localhost:8004"
ORDER_URL = "http://localhost:8001"
PAYMENT_URL = "http://localhost:8003"


@app.get("/search")
def search_products(q: str):
    r = requests.get(f"{CATALOGUE_URL}/search", params={"q": q})
    return r.json()


@app.post("/purchase")
def purchase_cart(request: dict):
    item = request["item"]
    qty = request["qty"]
    price = request["price"]

    # 1. Initialize order
    order_resp = requests.post(f"{ORDER_URL}/order", json={"item": item, "qty": qty})
    order = order_resp.json()

    # 2. Proceed to payment
    pay_resp = requests.post(f"{PAYMENT_URL}/pay", json={"order_id": order["order_id"], "amount": price})
    pay = pay_resp.json()

    # 3. Return combined result
    return {
        "order_id": order["order_id"],
        "reservation_status": order["final_status"],
        "payment_status": pay["status"]
    }
