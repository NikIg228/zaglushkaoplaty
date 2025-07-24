from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

mock_orders = {}

@app.post("/create-payment")
async def create_payment(request: Request):
    data = await request.json()
    order_id = str(uuid4())
    payment_url = f"https://your-domain.com/payment/{order_id}"
    mock_orders[order_id] = {
        "product_name": data.get("product_name"),
        "amount": data.get("amount"),
        "user_id": data.get("user_id"),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    return {"order_id": order_id, "payment_url": payment_url}

@app.get("/payment/{order_id}", response_class=HTMLResponse)
async def payment_page(order_id: str):
    if order_id not in mock_orders:
        return HTMLResponse("<h1>Order not found</h1>", status_code=404)

    product = mock_orders[order_id]
    html = f"""
<html>
    <head><title>Оплата</title></head>
    <body style='font-family: sans-serif; text-align: center; padding: 40px;'>
        <h1>Оплата услуги: {product["product_name"]}</h1>
        <p>Сумма к оплате: {product["amount"]} ₸</p>
        <form action='/confirm-payment' method='post'>
            <input type='hidden' name='order_id' value='{order_id}'>
            <button type='submit' style='padding: 10px 20px; font-size: 16px;'>Оплатить</button>
        </form>
    </body>
</html>
"""
    return HTMLResponse(content=html)

@app.post("/confirm-payment")
async def confirm_payment(order_id: str = Form(...)):
    if order_id in mock_orders:
        mock_orders[order_id]["status"] = "paid"
        return RedirectResponse(url=f"/update-order-status?order_id={order_id}&status=paid", status_code=302)
    return HTMLResponse("<h1>Order not found</h1>", status_code=404)

@app.get("/update-order-status")
async def update_order_status(order_id: str, status: str):
    if order_id in mock_orders:
        mock_orders[order_id]["status"] = status
        return JSONResponse({"message": f"Order {order_id} status updated to {status}"})
    return JSONResponse({"error": "Order not found"}, status_code=404)