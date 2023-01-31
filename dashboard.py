import asyncio
from fastapi import APIRouter,Request,HTTPException
router = APIRouter()
from auth import verify
from utils import check_user_exists_using_email
