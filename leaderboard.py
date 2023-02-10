from bson import ObjectId
import os
from utils import check_user_exists_using_email
from auth import verify
import asyncio
from fastapi import APIRouter, Request, HTTPException
import pymongo
router = APIRouter()

MONGO_URI = os.environ.get('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)
db = client["BetaLabs-Portal"]

router = APIRouter()


@router.get('/leaderboard/all')
def get_overall_leaderboard(req: Request, q, page: int = 0, per_page: int = 10):
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
        query["name"] = {"$regex": q, "$options": "i"}
    result = {'meta': {}, 'data': {}}
    result['meta'] = {'q': q, 'page': page, 'per_page': per_page, 'total': 0}
    fetch_users = db['users'].find(query).sort(
        [('score', -1), ('name', 1)]).skip((page-1)*per_page).limit(per_page)
    fetch_count = db['users'].count_documents(query)
    result['meta']['total'] = fetch_count
    result['data'] = []
    for user in fetch_users:
        user['_id'] = str(user.get("_id", None))
        user_details = {}
        user_details['rank'] = user.get("rank", None)
        user_details['name'] = user.get("name", None)
        user_details['score'] = user.get("score", None)
        user_details['photo'] = user.get("photo", None)
        result['data'].append(user)
    return result


@router.get('/leaderboard/{event_id}')
def get_leaderboard(req: Request, id, page, per_page):
    user = asyncio.run(verify(req.headers.get("Authorization")))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_email = user.get("email", None)
    if not user_email:
        raise HTTPException(status_code=400, detail="User Email Not Found")
    fetch_user = check_user_exists_using_email(user_email)
    if not fetch_user:
        raise HTTPException(status_code=400, detail="User Not Found")
    fetch_event = db['events'].find_one({"_id": ObjectId(id)})
    if not fetch_event:
        raise HTTPException(status_code=400, detail="Event Not Found")
    fetch_event_type = fetch_event.get("type", None)
    if fetch_event_type != "assessment":
        raise HTTPException(
            status_code=404, detail="No Winners For This Event")
    fetch_winners = fetch_event.get("winners", [])
    if not fetch_winners:
        raise HTTPException(status_code=400, detail="No Winners Yet")
    result = {'meta': {}, 'data': {}}
    result['meta'] = {'event_id': id, 'page': page, 'per_page': per_page}
    result['data'] = []
    for winner in fetch_winners:
        fetch_user = db['users'].find_one({"_id": ObjectId(winner)})
        if fetch_user:
            fetch_user['_id'] = str(fetch_user.get("_id", None))
            result['data'].append(fetch_user)
    return result
