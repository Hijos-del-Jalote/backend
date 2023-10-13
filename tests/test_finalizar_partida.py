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

async def wait_ws(websocket):
    response = await websocket.receive_json()
    return json.loads(response)

async def test_finalizar_partida():
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
            if j.Rol != "lacosa":
                j.Rol = "infectado"
            else:
                j.isAlive = True
            ultimojugador = j
            ganadores.append(j.id)
            if j.Posicion == partida.turnoActual:
                jugadorActual = j
        j.Rol = "lacosa"
        j.isAlive = True
        idcarta = list(jugadorActual.cartas)[0].id
        # ultimojugador.Rol = "humano"
        commit()
        assert partida.finalizada == False
        
        with client1.websocket_connect("ws://localhost:8000/partidas/3/ws") as websocket:
            res = await wait_ws(websocket)
            response2 = await client2.post(f'cartas/jugar?id_carta={idcarta}')
            assert(response2.status_code == 200)
            
            # TAMBIEN PROBE ESTO:    
            # tasks = [wait_ws(websocket), client2.post(f'cartas/jugar?id_carta={idcarta}')]
            # res, response2 = await asyncio.gather(*tasks)
            
            # por ahora este json debe ser el de finalizar de partida ya que es el unico en jugar carta de ws,
            # desp si se agrega el de jugar carta, se cambia esto
            ####### Se queda esperando aca
            
            #######
            print("BBBBBBBBBBBBBBBBBBBBBBB")
            assert res == {"event": "finalizar", "data": json.dumps({'isHumanoTeamWinner': False, 'winners': sorted(ganadores)})}
        
        with db_session:
            assert Partida.get(id=partida.id).finalizada == True