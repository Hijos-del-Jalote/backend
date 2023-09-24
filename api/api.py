from fastapi import FastAPI
import sys
from .router.cartas import cartas_router
from .router.jugadores import jugadores_router
from .router.partidas import partidas_router

app = FastAPI()

app.include_router(cartas_router, prefix="/cartas", tags=["cartas"])
app.include_router(jugadores_router, prefix="/jugadores", tags=["jugadores"])
app.include_router(partidas_router, prefix="/partidas", tags=["partidas"])