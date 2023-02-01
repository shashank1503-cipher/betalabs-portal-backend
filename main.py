import asyncio
import json
import pymongo
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
import auth,dashboard,leaderboard,admin
from firebase_admin import auth as admin_auth

import os
MONGO_URI = os.environ.get('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)
db = client["BetaLabs-Portal"]
app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000"
    "https://betalabs-portal-backend-production.up.railway.app/",
    "https://betalabs-portal-backend-production.up.railway.app",
    "https://betalabs-portal.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"Let's": "Go"}    
app.include_router(auth.router)
app.include_router(leaderboard.router)
app.include_router(dashboard.router)
app.include_router(admin.router)

