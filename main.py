from cProfile import run
import sys, inspect
from fastapi import Request, FastAPI, status, HTTPException, Response, Depends
from pydantic import BaseModel
from typing import List
import uvicorn
from config.database import SessionLocal, engine, get_db
import config.models 
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import http.client
import time
from collections import Counter
import os
from dotenv import load_dotenv, find_dotenv
import json

load_dotenv(find_dotenv('/config/'))

X_AUTH = os.getenv('X_AUTH')

print(X_AUTH)

config.models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class loyaltyPoints(BaseModel):
    cid:str
    store:str
    cart_id:str
    # redeem_point:int
    # point:int
    class Config:   
        orm_mode=True
class productItem(BaseModel):
    pid:str
    store_hash:str
    qty:str
    group_id:str
    data:list
    class Config:   
        orm_mode=True

class Delivery(BaseModel): #serialser
    id:int
    delivery_date:str
    delivery_slot:int
    class Config:   
        orm_mode=True

class UpdateDelivery(BaseModel):
    store_hash:str
    up_date:str
    cart_id:str
    class Config:   
        orm_mode=True

#  DELIVERY DATES
@app.get("/api/v3/delivery_instruction_date/")
def get_delivery_dates(store_hash:str, db: Session = Depends(get_db)):
# CHECK STORE
    if store_hash == "ipw9t98930":
    # GET DELIVERY DATES AND CURRENT TIME
        deliveries = db.query(config.models.Delivery).limit(14)
        currentTime = time.strftime("%H")
        curernt_date_enabled = True
        if int(currentTime) > 12:
            curernt_date_enabled = False
    # DELIVERY SLOTS DICTIONARY
        # print(curernt_date_enabled)
        delivery_slots_available = {}
        for deliverydata in deliveries:
            delivery_slots_available[deliverydata.delivery_date] = deliverydata.delivery_slot  
        data_output = {"data":delivery_slots_available,"delivery_dates_off":"2022-12-25,2022-12-26,2022-12-23,2022-12-24,2022-12-27,2022-12-28,2022-12-29,2022-12-30,2022-12-31,2023-01-03","delivery_limit":"200","is_current_date_enabled":curernt_date_enabled,"max_date":15}
        data = jsonable_encoder(data_output)
        # print(delivery_slots_available)
        # print(data_output)
        return JSONResponse(content=data)
    else:
         return {"Error":"Incorrect store"}

    
@app.put("/api/v3/delivery_date_update/")
async def update_delivery_date(update: UpdateDelivery):
# CHECK STORE
    if update.store_hash == "ipw9t98930":
    # UPDATE DELIVERY SLOTS (CUSTOMER MESSAGE) ON BIGCOMMERCE ORDER
        conn = http.client.HTTPSConnection("api.bigcommerce.com")
        payload = '{\n"customer_message":"'+ update.up_date + '"\n}'
        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json",
            'X-Auth-Token':X_AUTH
            }
        conn.request("PUT", "/stores/"+update.store_hash+"/v3/checkouts/"+update.cart_id+"", payload, headers)
        # res = conn.getresponse()
        # data = res.read()
        # print(data.decode("utf-8"))
    else:
        return {"Error":"Incorrect store"}


# VALIDATE PRODUCT QTY

@app.post("/api/v3/validate_product/")
async def validate_products(item:productItem):
    # VARIABLES
    isCheckout = False
    cartMessage = ''

    # CHECK PRODUCTS FOR TRIAL, ACCESSORIES, SUPPLEMENTS (PRODUCT ID'S)
    productId_list = list(filter(None,item.pid.split(',')))
    productId_excempt = "244 234 231"
    if any(substring in productId_excempt for substring in productId_list):
        return {"data":"Success","ischeckout":True,"message":"product exempt"}

    # TOTAL PRODUCTS
    ProductKeyList = item.data
    totalProducts = Counter()
    for d in ProductKeyList:
        for key, value in d.items():
            totalProducts[key] += int(value)
    ProductTotal = sum(totalProducts.values())

    if isCheckout == False:
        if ProductTotal < 10:
                isCheckout = False
                cartMessage = "You must have a minimum of 10 items in your cart."
        else :
            isCheckout = True

    # CHECK OTHER PRODUCTS (PRODUCT ID'S)
    productId_excempt_other = "188 235 240 236 229 225 221 192 189 185"
    if any(substring in productId_excempt_other for substring in productId_list):
        # CHECK IF ONLY PRODUCT
        if len(productId_list) < 2:
            return {"data":"Success","ischeckout":True,"message":"product other"}
    
    # OUTPUT
    return {"data":"Success","ischeckout":isCheckout,"message":cartMessage}


# LOYALTY POINTS

@app.post("/api/v3/show_loyalty_point/")
async def show_loyalty_points(showLoyalty:loyaltyPoints):
    # GET POINTS FROM BC USER DATA
    conn = http.client.HTTPSConnection("api.bigcommerce.com")
    headers = {
        'Content-Type': "",
        'Accept': "",
        'X-Auth-Token': X_AUTH
        }
    conn.request("GET", "/stores/"+showLoyalty.store+"/v3/customers/form-field-values?customer_id="+showLoyalty.cid+"", headers=headers)
    res = conn.getresponse()
    data = json.loads(res.read()) 
    pointsData = data.get('data')
    pointCurrency = "{:.2f}".format(pointsData[0]["value"]/100)
    return {"message":"Use "+str(pointsData[0]["value"])+" Points for a "+str(pointCurrency)+" discount on this order!","monetry_point":"2.00","total_point":str(pointsData[0]["value"])}



   