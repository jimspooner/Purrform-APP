from cProfile import run
from fastapi import Request, FastAPI, status, HTTPException, Response, Depends
from pydantic import BaseModel
from typing import List
from config.database import SessionLocal, engine, get_db
import config.models 
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

# local env
# load_dotenv(find_dotenv('/config/'))
# kinsta env
load_dotenv(find_dotenv())

X_AUTH = os.getenv('X_AUTH')

# print(X_AUTH)

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

class stockists(BaseModel):
    title:str
    add:str
    city:str
    zip:str
    country:str
    email:str
    url:str
    iso:str
    lat:str
    lng:str
    
    class Config:   
        orm_mode=True
class loyaltyPoints(BaseModel):
    created_at:str
    customer_id:int
    mode:str
    new_point:str
    old_point:int
    order_id:int
    status:str
    type:str
    updated_at:str
    class Config:   
        orm_mode=True

class showPoints(BaseModel):
    store_hash:str
    cid:str
    checkout_id:str

    class Config:   
        orm_mode=True

class redeemPoints(BaseModel):
    store_hash:str
    cid:str
    checkout_id:str
    redeem_point:str

    class Config:   
        orm_mode=True

class removePoints(BaseModel):
    store_hash:str
    cid:str
    checkout_id:str
    point:str

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

class UpdateCustomer(BaseModel):
    producer:str
    hash:str
    created_at:str
    store_id:str
    scope:str
    data:List

    class Config:   
        orm_mode=True

#  DELIVERY DATES

@app.get("/api/v3/delivery_instruction_date/")
async def get_delivery_dates(store_hash:str, db: Session = Depends(get_db)):
    # CHECK STORE
    if store_hash == "ipw9t98930":
        # GET DELIVERY DATES AND CURRENT TIME
        deliveries = db.query(config.models.Delivery).limit(14)
        currentTime = time.strftime("%H")
        curernt_date_enabled = True
        if int(currentTime) > 12:
            curernt_date_enabled = False
        # DELIVERY SLOTS DICTIONARY

        delivery_slots_available = {}
        for deliverydata in deliveries:
            delivery_slots_available[deliverydata.delivery_date] = deliverydata.delivery_slot  
        data_output = {"data":delivery_slots_available,"delivery_dates_off":"2023-01-18,2022-12-26,2022-12-23,2022-12-24,2022-12-27,2022-12-28,2022-12-29,2022-12-30,2022-12-31,2023-01-03","delivery_limit":"200","is_current_date_enabled":curernt_date_enabled,"max_date":15}
        data = jsonable_encoder(data_output)

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
async def show_loyalty_points(showLoyalty:showPoints):
    # GET POINTS FROM BC USER DATA
    conn = http.client.HTTPSConnection("api.bigcommerce.com")
    conn1 = http.client.HTTPSConnection("api.bigcommerce.com")
    headers = {
        'Content-Type': "",
        'Accept': "",
        'X-Auth-Token': X_AUTH
        }
    # GET CHECKOUT FROM ID
    conn1.request("GET", "/stores/"+showLoyalty.store_hash+"/v3/checkouts/"+showLoyalty.checkout_id, headers=headers)
    # GET LOYALTY POINTS FROM BC CUSTOMER POINTS
    conn.request("GET", "/stores/"+showLoyalty.store_hash+"/v3/customers/form-field-values?customer_id="+showLoyalty.cid+"", headers=headers)
    res1 = conn1.getresponse()
    res = conn.getresponse()
    data1 = json.loads(res1.read())
    data = json.loads(res.read()) 
    discountAmount = data1['data']['cart']['discount_amount']

    # CHECK IF CUSTOMER HAS ALREADY ADDED POINTS TO CART
    if discountAmount > 0:
        return {}
    else :
        pointsData = data.get('data')
        pointCurrency = "{:.2f}".format(pointsData[0]["value"]/100)
        return {"message":"Use "+str(pointsData[0]["value"])+" Points for a &pound"+str(pointCurrency)+" discount on this order!","monetry_point":"2.00","total_point":str(pointsData[0]["value"])}


@app.get("/api/v3/earn_LP/")
def get_loyalty_points(store_hash:str, cust_id:str, db: Session = Depends(get_db)):
    # CHECK STORE
    if store_hash == "ipw9t98930":
        # GET LOYALTY POINTS API DATABASE
        points = db.query(config.models.Points).filter(config.models.Points.customer_id == cust_id).all()
        # CALC TOTAL POINTS FROM API DATABASE
        total_points = 0
        for point in points:
            if point.status == 'EARNED':
                intPoint = point.new_point.replace('+','')
                total_points = total_points+int(intPoint)
            if point.status == 'REDEEMED':
                intPoint = point.new_point.replace('-','')
                total_points = total_points-int(intPoint)

        points_output = {"Data":points,"total_points":total_points}
        data = jsonable_encoder(points_output)
        
        return data
    else:
        return {"Error":"Incorrect store"}


@app.post("/api/v3/redeem_loyalty_point/")
def redeem_loyalty_points(redeemLoyalty:redeemPoints):
    # ADD DISCOUNT TO CHECKOUT ID
    conn = http.client.HTTPSConnection("api.bigcommerce.com")
    cartDiscount = (int(redeemLoyalty.redeem_point)/100)
    redeem_points = str(cartDiscount)
    store_hash = redeemLoyalty.store_hash
    checkout_id = redeemLoyalty.checkout_id

    payload = "{\n  \"cart\": {\n    \"discounts\": [\n      {\n        \"discounted_amount\": "+redeem_points+",\n        \"name\": \"manual\"\n      }\n    ]\n  }\n}"
    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json",
        'X-Auth-Token': X_AUTH
        }

    conn.request("POST", "/stores/"+store_hash+"/v3/checkouts/"+checkout_id+"/discounts", payload, headers)

    res = conn.getresponse()
    data = res.read()
        
    return data

@app.post("/api/v3/remove_loyalty_point/")
def remove_loyalty_points(removeLoyalty:removePoints):
    # REMOVE DISCOUNT TO CHECKOUT ID
    conn = http.client.HTTPSConnection("api.bigcommerce.com")
    store_hash = removeLoyalty.store_hash
    checkout_id = removeLoyalty.checkout_id
    point = removeLoyalty.point

    payload = "{\n  \"cart\": {\n    \"discounts\": [\n      {\n        \"discounted_amount\": "+point+",\n        \"name\": \"manual\"\n      }\n    ]\n  }\n}"
    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json",
        'X-Auth-Token': X_AUTH
        }

    conn.request("POST", "/stores/"+store_hash+"/v3/checkouts/"+checkout_id+"/discounts", payload, headers)

    res = conn.getresponse()
    data = res.read()
        
    return data

# STOCKIST
@app.get("/api/v3/stockist/")
async def stockists(store_hash:str, db: Session = Depends(get_db)):
    if store_hash == "ipw9t98930":
        # GET STOCKISTS
        stockist_list = db.query(config.models.stockists).all()
        
        return stockist_list
    else:
        return {"Error":"Incorrect store"}

# CAT BDAYS
@app.get("/api/v3/cat_reg/")
async def stockists(store_hash:str, cid:str, db: Session = Depends(get_db)):
    if store_hash == "ipw9t98930":
        # GET STOCKISTS
        cbday_list = db.query(config.models.catbday).all()
        
        return cbday_list
    else:
        return {"Error":"Incorrect store"}


# BC WEB HOOKS
@app.post("/webhook/v3/order_created")
async def order_created():
    # UPDATE DELIVERY LOG
    # UPDATE LOYALTY POINTS
    pass

@app.post("/webhook/v3/order_refund")
async def order_refund():
    # UPDATE LOYALTY POINTS
    pass

@app.post("/webhook/v3/order_update")
async def order_update():
    # UPDATE LOYALTY POINTS
    pass

@app.post("/webhook/v3/customer_update", status_code=200)
async def customer_update(updateLoyalty:UpdateCustomer):
    # UPDATE LOYALTY POINTS
    formField = updateLoyalty.data
    for item, val in formField.items():
        if item == 'id':
            cust_id = val
    conn = http.client.HTTPSConnection("api.bigcommerce.com")

    payload = "[\n  {\n    \"customer_id\": "+str(cust_id)+",\n    \"name\": \"Loyalty Points\",\n    \"value\": 500\n  }\n]"

    headers = {
        'Content-Type': "application/json",
        'X-Auth-Token': X_AUTH
        }

    conn.request("PUT", "/stores/ipw9t98930/v3/customers/form-field-values", payload, headers)

    res = conn.getresponse()
    data = res.read()

    return data

