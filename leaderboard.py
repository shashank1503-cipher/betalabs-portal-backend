import asyncio
from fastapi import APIRouter,Request,HTTPException
router = APIRouter()
from auth import verify
from utils import check_user_exists_using_email

router = APIRouter()

@router.get('/all')
def get_overall_leaderboard(req:Request,q,page,per_page):
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
        query["name"] = {"$regex":q,"$options":"i"}
        

def fetch_projects(req: Request,q:str,page:int=1,per_page:int=10):
  user = asyncio.run(verify(req.headers.get("Authorization")))
  if not user:
    raise HTTPException(status_code=401, detail="Unauthorized")
  user_email = user.get("email", None)
  if not user_email:
    raise HTTPException(status_code=400, detail="User Email Not Found")
  fetch_user = check_user_exists_using_email(user_email)
  if not fetch_user:
    raise HTTPException(status_code=400, detail="User Not Found")
  query = {"user_id":{"$ne":ObjectId(fetch_user['_id'])}}
  
  if q:
    query["title"] = {"$regex":q,"$options":"i"}
  fetch_projects = db["projects"].find(query).sort("created_at",-1).skip((page-1)*per_page).limit(per_page)
  fetch_count = db["projects"].count_documents(query)
  if not fetch_projects:
    raise HTTPException(status_code=404, detail="No Projects Found")
  result = []
  for i in list(fetch_projects):
    i['_id'] = str(i['_id'])
    fetch_user_id = fetch_user['_id']
    if fetch_user_id:
      i['user_id'] = str(i['user_id'])
    count_interested = db['projects'].count_documents({"_id":ObjectId(i['_id']),"interested_users":ObjectId(fetch_user_id)})
    if count_interested:
      i['interested'] = True
    if i.get("interested_users"):
      i.pop("interested_users")
    result.append(i)

  return {'meta':{'total_records':fetch_count,'page':page,'per_page':per_page}, 'data':result}