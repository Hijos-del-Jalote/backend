from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from api.router.partidas import *
from api.router.cartas import *
from db.models import *
from api.ws import *
import asyncio



async def test_jugar_whisky(cleanup_db_after_test):
    client = TestClient(app)
    with db_session:
        partida = Partida(nombre="partida", iniciada=True, finalizada=False , maxJug=5, minJug=4, turnoActual=1)
        db.commit()
        jugador = Jugador(nombre="Jugador", Rol="Humano", isHost=True, isAlive=True, blockIzq=False, blockDer=False, Posicion=0)
        db.commit()
        template_carta=TemplateCarta(nombre="Whisky", descripcion="Whisky", tipo="accion")
        template_carta2=TemplateCarta(nombre="Lanzallamas", descripcion="Whisky", tipo="accion")
        db.commit()
        carta_whisky = Carta(descartada=False, template_carta=template_carta, partida=partida, jugador=jugador)
        for i in range(4):
            Carta(descartada=False, template_carta=template_carta2 , partida=partida, jugador=jugador)
        db.commit()
        carta_whisky=Carta.get(id = carta_whisky.id)
        with client.websocket_connect(f"ws://localhost:8000/partidas/{partida.id}/ws?idJugador={jugador.id}") as websocket:
            while len(manager.active_connections.get(1, {})) != 1:
                await asyncio.sleep(0.1)
            assert len(manager.active_connections[1]) == 1
            response = client.post(f'cartas/jugar?id_carta={carta_whisky.id}') 
            assert response.status_code == 200
            response2 = websocket.receive_json()
            assert response2 == {"event": "Whisky", "data": get_mano_jugador(jugador.id)}

            