import os
from fastapi import  APIRouter, Request
import firebase_admin
from firebase_admin import auth, credentials
import json
from db import db, read_one, create

router = APIRouter()
credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
cred = credentials.Certificate(credentials_json)
firebase_admin.initialize_app(cred)

async def verify(authorization):
   
    try:
        id_token = authorization.split(" ")[1]
        user = auth.verify_id_token(id_token)
        
        
        return user
    except Exception as e:
        print(e)
        return False


@router.post('/auth/adduser')
async def addUser(req: Request):

    if verify(req.headers["authorization"]):
        print("YES")
    else:
        return {"error": "Not Authorized"}

    data = await req.body()
    data = json.loads(data)
    data = data['user']

    new_data = checkIfUserExists(data['g_id'])
    # print("Data 2: ", data)
    if not new_data:
        addUser(data)
        return {
            "message":"Added User",
            "code": 1
        }
    else:
        return {
            "data": data,
            "code": 2
        }


def checkIfUserExists(id):
    data = read_one(db, 'users', {'g_id':f'{id}'})
    if not data:
        return None    
    return data

    
def addUser(data):
   
    try:
        create(db, 'users', data)
    except:
        return {"error": "error adding user."}


@router.post('/auth/getUser')
async def getdata(req: Request):
    data = await req.body()
    id = json.loads(data)['g_id']
    print(id)

    if verify(req.headers["authorization"]):
        print("YES")
    else:
        return {"error": "Not Authorized"}

    user = checkIfUserExists(id)
    print(user)

    if not user:
        return {'error': 'error'}

    return {"user": {
        "name": user['name'],
        "email": user['email'],
        'photo': user['photo'],
        'g_id': user['g_id']
    }}