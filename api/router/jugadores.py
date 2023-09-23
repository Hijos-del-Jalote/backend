from fastapi import APIRouter
from pony.orm import db_session
from models import Jugador, Rol

jugadores_router = APIRouter() 


