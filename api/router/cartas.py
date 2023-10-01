from fastapi import APIRouter
from pony.orm import db_session
from db.models import *



cartas_router = APIRouter()
