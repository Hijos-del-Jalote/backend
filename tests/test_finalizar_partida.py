import pytest
import httpx
from db.partidas_session import get_partida, fin_partida_respond
from api.api import app
from fastapi.testclient import TestClient
from pony.orm import db_session, commit
from db.models import Jugador,Partida
from tests.test_newplayer import random_user
from api.ws import manager
import json
from typing import List
import asyncio
from .test_robar_carta import vaciar_manos

async def test_finalizar_partida(cleanup_db_after_test):
    client1 = TestClient(app)
    client2 = TestClient(app)
    
    response = client2.post(f'jugadores?nombre={"J" + str(0)}')
    hostid = response.json()["id"]
    client2.post(f'partidas/?nombrePartida=partida&idHost={hostid}')
    with db_session:
        partida = Jugador.get(id=hostid).partida
    
    # mandar un post con otro cliente:
    for i in range(1,4):
        response = client2.post(f'jugadores?nombre={"J" + str(i)}')
        client2.post(f'partidas/unir?idPartida={partida.id}&idJugador={response.json()["id"]}')

    response = client2.put(f'partidas/iniciar?idPartida={partida.id}')
    
    # Esperar la respuesta del websocket en el cliente1:
    ganadores = []
    with db_session:
        partida = Partida.get(id=partida.id)
        for j in partida.jugadores:
            j.Rol = "Humano"
            j.isAlive = True
            ganadores.append(j.id)
            if j.Posicion == partida.turnoActual:
                jugadorActual = j
            else:
                lacosa = j # se lo asigno a uno que no sea el que le toca
            
        lacosa.Rol = "La cosa"
        lacosa.isAlive = False
        idlacosa = lacosa.id
        ganadores.remove(lacosa.id)
        idcarta = list(jugadorActual.cartas)[0].id
        commit()
        assert partida.finalizada == False
        
        
    with client1.websocket_connect(f"ws://localhost:8000/partidas/{partida.id}/ws?idJugador={idlacosa}") as websocket:
        
        response2 = client2.post(f'cartas/jugar?id_carta={idcarta}&id_objetivo={idlacosa}')
        assert(response2.status_code == 200)

        response = websocket.receive_json()
        # {"event": "finalizar", "data": json.dumps({'isHumanoTeamWinner': True, 'winners': sorted(ganadores)})}
        assert response == {"event": "finalizar", "data": json.dumps({'isHumanoTeamWinner': True, 'winners': sorted(ganadores)},
                                         separators=(',',':'))}
        
        with db_session:
            assert Partida.get(id=partida.id).finalizada == True