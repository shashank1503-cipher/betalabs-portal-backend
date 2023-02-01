import asyncio
from fastapi import APIRouter,Request,HTTPException
import pymongo
from bson import ObjectId
from auth import verify
from utils import check_user_exists_using_email
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
MONGO_URI = os.environ.get('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)
db = client["BetaLabs-Portal"]

router = APIRouter()

@router.get("/events")
def events(req:Request,q:str = None,page:int=0,per_page:int=10,upcoming:str = "all"):
    user = asyncio.run(verify(req.headers.get("Authorization")))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_email = user.get("email", None)
    if not user_email:
        raise HTTPException(status_code=400, detail="User Email Not Found")
    fetch_user = check_user_exists_using_email(user_email)
    if not fetch_user:
        raise HTTPException(status_code=400, detail="User Not Found")
    query = {}
    if q:
        query["eventName"] = {"$regex":q,"$options":"i"}
    if upcoming == "past":
        query["eventEnd"] = {"$lte":datetime.now()}
    elif upcoming == "future":
        query["eventStart"] = {"$gte":datetime.now()}
    fetch_events = db["events"].find(query).skip(page*per_page).limit(per_page)
    fetch_count = db["events"].count_documents(query)
    result = {"meta":{},"data":[]}
    result["meta"] = {'total':fetch_count,"page":page,"per_page":per_page,"upcoming":upcoming}
    data = []
    for event in fetch_events:
        event["_id"] = str(event["_id"])
        data.append(event)
    result["data"] = data
    return result

@router.get("/events/{eventId}")
def eventFind(req:Request,eventId):
    user = asyncio.run(verify(req.headers.get("Authorization")))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_email = user.get("email", None)
    if not user_email:
        raise HTTPException(status_code=400, detail="User Email Not Found")
    fetch_user = check_user_exists_using_email(user_email)
    if not fetch_user:
        raise HTTPException(status_code=400, detail="User Not Found")
    if not ObjectId.is_valid(eventId):
        raise HTTPException(status_code=400,detail="Galat Id h Bsdike")
    event=db["events"].find_one({"_id" : ObjectId(eventId)})
    user_attending = db["attendance"].find_one({"userId":ObjectId(fetch_user["_id"]),"eventId":ObjectId(event["_id"])})
    event["user_attending"] = False
    if user_attending:
        event["user_attending"] = True
    if not event:
        raise HTTPException(status_code=400,detail="Event Exist Nahi krta kal aana")
    event['_id'] = str(event['_id'])
    return event
@router.post("/events/{eventId}/submitattendance")
def submitAttendance(req:Request,eventId):
    user = asyncio.run(verify(req.headers.get("Authorization")))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_email = user.get("email", None)
    if not user_email:
        raise HTTPException(status_code=400, detail="User Email Not Found")
    fetch_user = check_user_exists_using_email(user_email)
    if not fetch_user:
        raise HTTPException(status_code=400, detail="User Not Found")
    if not ObjectId.is_valid(eventId):
        raise HTTPException(status_code=400,detail="Galat Id h Bsdike")
    event=db["events"].find_one({"_id" : ObjectId(eventId)})
    if not event:
        raise HTTPException(status_code=400,detail="Event Exist Nahi krta kal aana")
    event['_id'] = str(event['_id'])
    if not event.get("attendance_status",False):
        raise HTTPException(status_code=400,detail="Attendance Not Allowed")
    data ={}
    data["userId"] = ObjectId(fetch_user["_id"])
    data["eventId"] = ObjectId(event["_id"])
    fetch_attendance = db["attendance"].find_one(data)
    if fetch_attendance:
        raise HTTPException(status_code=400,detail="Attendance already submitted")
    try:
        db["attendance"].insert_one(data)
        return {"message":"Attendance Submitted"}
    except Exception as e:
        raise HTTPException(status_code=500,detail="Internal Server Error")
@router.get("/techsprint")
def techsprint(req:Request,):
    user = asyncio.run(verify(req.headers.get("Authorization")))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_email = user.get("email", None)
    if not user_email:
        raise HTTPException(status_code=400, detail="User Email Not Found")
    fetch_user = check_user_exists_using_email(user_email)
    if not fetch_user:
        raise HTTPException(status_code=400, detail="User Not Found")
    fetch_ts = db["techsprints"].find_one({'current':True})
    data = {}
    if not fetch_ts:
        data['techsprint'] = "No Techsprint is going on"
        return data
    data['techsprint'] = fetch_ts['name']
    return data