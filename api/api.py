from fastapi import FastAPI
from api.router.cartas import cartas_router
from api.router.jugadores import jugadores_router
from api.router.partidas import partidas_router, websocket_endpoint, websocket_endpoint_chat

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurar CORS para permitir todas las solicitudes (en desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cartas_router, prefix="/cartas", tags=["cartas"])
app.include_router(jugadores_router, prefix="/jugadores", tags=["jugadores"])
app.include_router(partidas_router, prefix="/partidas", tags=["partidas"])

app.add_websocket_route("/partidas/{id}/ws", websocket_endpoint)
app.add_websocket_route("/partidas/{id}/ws/chat", websocket_endpoint_chat)