from fastapi import APIRouter
from pony.orm import db_session
from db.models import db

cartas_router = APIRouter()
