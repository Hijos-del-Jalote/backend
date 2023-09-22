from fastapi import APIRouter
from pony.orm import db_session
from db.models import Partida

partidas_router = APIRouter()
 