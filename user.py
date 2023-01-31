from utils import check_user_exists_using_email
from auth import verify
import asyncio
from fastapi import APIRouter, Request, HTTPException
router = APIRouter()


@router.get('/details')
def first_time_login(req: Request):
    user = asyncio.run(verify(req.headers.get("Authorization")))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_email = user.get("email", None)
    if not user_email:
        raise HTTPException(status_code=400, detail="User Email Not Found")
    fetch_user = check_user_exists_using_email(user_email)
    if not fetch_user:
        raise HTTPException(status_code=400, detail="User Not Found")
    result = {'meta': {}, 'data': {}}
    result['meta'] = {'user_id':str(fetch_user.get("_id",None))}
    fetch_user['_id'] = str(fetch_user.get("_id",None))
    result["data"] = fetch_user
    return result




