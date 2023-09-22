from fastapi import APIRouter
from pony.orm import db_session
from db.models import Jugador, Rol

jugadores_router = APIRouter() 