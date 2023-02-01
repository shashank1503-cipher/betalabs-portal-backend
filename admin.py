import asyncio
from fastapi import APIRouter,Request,HTTPException
import pymongo
from bson import ObjectId
from auth import verify
from utils import check_user_exists_using_email
import os
from datetime import datetime
import json
from firebase_admin import auth as admin_auth
MONGO_URI = os.environ.get('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)
db = client["BetaLabs-Portal"]

router = APIRouter()

@router.post("/admin/event")
async def create_event(req:Request):
    user = None
    authorization  = req.headers.get("Authorization")
    try:
            id_token = authorization.split(" ")[1]
            user = admin_auth.verify_id_token(id_token)
    except Exception as e:
            print(e)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_email = user.get("email", None)
    if not user_email:
        raise HTTPException(status_code=400, detail="User Email Not Found")
    if user_email != "techclub@iiitkottayam.ac.in":
        raise HTTPException(status_code=401, detail="Unauthorized")
    data = await req.body()
    if data:
        data = json.loads(data)
    event_name = data.get("eventName",None)
    event_type = data.get("eventType",None)
    event_category = data.get("eventCategory",None)
    event_start = data.get("eventStart",None)
    event_end = data.get("eventEnd",None)
    event_taker = data.get("eventTaker",None)
    event_description = data.get("eventDescription",None)
    event_image = data.get("eventImage",None)
    event_rules = data.get("eventRules",None)
    event_prizes = data.get("eventPrizes",None)
    event_timing =  data.get("eventTiming",None)
    if not event_name:
        raise HTTPException(status_code=400, detail="Event Name Not Found")
    if not event_taker:
        raise HTTPException(status_code=400, detail="Event Taker Not Found")
    if not event_type:
        raise HTTPException(status_code=400, detail="Event Type Not Found")
    if not event_category:
        raise HTTPException(status_code=400,detail="Event Category Not Found")
    if not event_start:
        raise HTTPException(status_code=400, detail="Event Start Date Not Found")
    if not event_end:
        raise HTTPException(status_code=400, detail="Event End Date Not Found")
    event_start_datetime = datetime.strptime(event_start, '%d/%m/%Y')
    event_end_datetime = datetime.strptime(event_end, '%d/%m/%Y')
    event = {
        "eventName":event_name,
        "eventTaker":event_taker,
        "eventCategory":event_type,
        "start":event_start,
        "end":event_end,
        "eventStart":event_start_datetime,
        "eventEnd":event_end_datetime,
        "description":event_description,
        "rules":event_rules,
        "prizes":event_prizes,
        "winners":[],
        "image":event_image,
        "attendance_status":False,
        "timing":event_timing,
    }
    try:
        db['events'].insert_one(event)
        return {"message":"Event Created Successfully"}
    except:
        raise HTTPException(status_code=500, detail="Error Adding Event")
@router.put('/admin/event/{id}')
async def edit_event(req:Request,id:str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid Id")
    user = None
    authorization  = req.headers.get("Authorization")
    try:
            id_token = authorization.split(" ")[1]
            user = admin_auth.verify_id_token(id_token)
    except Exception as e:
            print(e)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_email = user.get("email", None)
    if not user_email:
        raise HTTPException(status_code=400, detail="User Email Not Found")
    if user_email != "techclub@iiitkottayam.ac.in":
        raise HTTPException(status_code=401, detail="Unauthorized")
    data = await req.body()
    if data:
        data = json.loads(data)
    event = {}
    event_name = data.get("eventName",None)
    event_type = data.get("eventType",None)
    event_category = data.get("eventCategory",None)
    event_description = data.get("eventDescription",None)
    event_image = data.get("eventImage",None)
    event_rules = data.get("eventRules",None)
    event_prizes = data.get("eventPrizes",None)
    event_start = data.get("eventStart",None)
    event_end = data.get("eventEnd",None)
    event_start_datetime = datetime.strptime(event_start, '%d/%m/%Y')
    event_end_datetime = datetime.strptime(event_end, '%d/%m/%Y')
    event_timing = data.get("eventTiming",None)
    if event_name:
        event["eventName"] = event_name
    if event_type:
        event["eventType"] = event_type
    if event_category:
        event["eventCategory"] = event_category
    if event_description:
        event["eventDescription"] = event_description
    if event_image:
        event["eventImage"] = event_image
    if event_rules:
        event["eventRules"] = event_rules
    if event_prizes:
        event["eventPrizes"] = event_prizes
    if event_start:
        event["start"] = event_start
        event["eventStart"] = event_start_datetime
    if event_end:
        event["end"] = event_end
        event["eventEnd"] = event_end_datetime
    if event_timing:
        event["eventTiming"] = event_timing

    if not event:
        raise HTTPException(status_code=400, detail="No Data Found")
    try:
        db['events'].update_one({"_id":ObjectId(id)}, {"$set":event})
        return {"message":"Event Updated Successfully"}
    except:
        raise HTTPException(status_code=500, detail="Error Updating Event")
@router.delete('/admin/event/{id}')
async def delete_event(req:Request,id:str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid Id")
    user = None
    authorization  = req.headers.get("Authorization")
    try:
            id_token = authorization.split(" ")[1]
            user = admin_auth.verify_id_token(id_token)
    except Exception as e:
            print(e)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_email = user.get("email", None)
    if not user_email:
        raise HTTPException(status_code=400, detail="User Email Not Found")
    if user_email != "techclub@iiitkottayam.ac.in":
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        db['events'].delete_one({"_id":ObjectId(id)})
        return {"message":"Event Deleted Successfully"}
    except:
        raise HTTPException(status_code=500, detail="Error Deleting Event")
@router.put('/admin/event/{id}/attendance')
async def attendance(req:Request,id:str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid Id")
    user = None
    authorization  = req.headers.get("Authorization")
    try:
            id_token = authorization.split(" ")[1]
            user = admin_auth.verify_id_token(id_token)
    except Exception as e:
            print(e)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_email = user.get("email", None)
    if not user_email:
        raise HTTPException(status_code=400, detail="User Email Not Found")
    if user_email != "techclub@iiitkottayam.ac.in":
        raise HTTPException(status_code=401, detail="Unauthorized")
    data = await req.body()
    if data:
        data = json.loads(data)
    attendance_status = data.get("attendanceStatus",None)
    if attendance_status is None:
        raise HTTPException(status_code=400, detail="Attendance Status Not Found")
    try:
        db['events'].update_one({"_id":ObjectId(id)}, {"$set":{"attendance_status":attendance_status}})
        return {"message":"Attendance Status Updated Successfully"}
    except:
        raise HTTPException(status_code=500, detail="Error Updating Attendance Status")

@router.put('/admin/event/{id}/winner')
async def winner(req:Request,id:str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid Id")
    user = None
    authorization  = req.headers.get("Authorization")
    try:
            id_token = authorization.split(" ")[1]
            user = admin_auth.verify_id_token(id_token)
    except Exception as e:
            print(e)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_email = user.get("email", None)
    if not user_email:
        raise HTTPException(status_code=400, detail="User Email Not Found")
    if user_email != "techclub@iiitkottayam.ac.in":
        raise HTTPException(status_code=401, detail="Unauthorized")
    data = await req.body()
    if data:
        data = json.loads(data)
    winner = data.get("winner",None)
    if not winner:
        raise HTTPException(status_code=400, detail="Winner Not Found")
    try:
        db['events'].update_one({"_id":ObjectId(id)}, {"$set":{"winners":winner}})
        return {"message":"Winner Added Successfully"}
    except:
        raise HTTPException(status_code=500, detail="Error Adding Winner")