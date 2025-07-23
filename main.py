from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import List

# Load env vars
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# ---------------------
# DATA MODELS
# ---------------------
class PriceUpdate(BaseModel):
    product_name: str
    your_price: float
    competitor_prices: List[float]
    price_floor_pct: float
    undercut_amount: float
    user_id: str

class ProductOut(BaseModel):
    product_name: str
    suggested_price: float
    floor_price: float
    user_id: str

# ---------------------
# PRICE CALCULATION
# ---------------------
def calculate_price(data: PriceUpdate):
    lowest_comp = min(data.competitor_prices)
    floor = data.your_price * data.price_floor_pct / 100
    new_price = max(lowest_comp - data.undercut_amount, floor)
    return round(new_price, 2), round(floor, 2)

# ---------------------
# API ROUTES
# ---------------------
@app.post("/save-product")
def save_product(data: PriceUpdate):
    try:
        suggested, floor = calculate_price(data)
        response = supabase.table("products").insert({
            "product_name": data.product_name,
            "suggested_price": suggested,
            "floor_price": floor,
            "user_id": data.user_id
        }).execute()

        return {
            "status": "success",
            "product": data.product_name,
            "suggested_price": suggested,
            "floor_price": floor
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products/{user_id}", response_model=List[ProductOut])
def get_products(user_id: str):
    try:
        result = supabase.table("products").select("*").eq("user_id", user_id).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
