from fastapi import APIRouter
from pony.orm import db_session
from models import Carta, TemplateCarta, Tipo_Carta

cartas_router = APIRouter()
