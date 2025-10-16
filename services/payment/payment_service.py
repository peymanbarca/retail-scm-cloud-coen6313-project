from fastapi import FastAPI
import random
import time

app = FastAPI(title="Mock Payment Service")


@app.post("/pay")
def process_payment(request: dict):
    order_id = request.get("order_id")
    amount = request.get("amount", 0.0)
    time.sleep(1)  # simulate processing delay

    # Randomly approve or reject
    success = random.choice([True, True, True, False])
    status = "SUCCESS" if success else "FAILED"
    return {"order_id": order_id, "amount": amount, "status": status}
