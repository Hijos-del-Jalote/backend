import pytest
import httpx
from db.partidas_session import get_partida
from api.api import app
from fastapi.testclient import TestClient
from pony.orm import db_session, commit
from db.models import Jugador,Partida
from tests.test_newplayer import random_user
from api.ws import manager
from typing import List

from .test_robar_carta import vaciar_manos

async def test_finalizar_partida():
    client1 = TestClient(app)
    client2 = TestClient(app)

    with client1.websocket_connect("ws://localhost:8000/partidas/3/ws") as websocket:
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
        
        with db_session:
            partida = Partida.get(id=partida.id)
            for j in partida.jugadores:
                if j.Rol != "lacosa":
                    j.Rol = "infectado"
                    ultimojugador = j
                if j.Posicion == partida.turnoActual:
                    jugadorActual = j
            idcarta = list(jugadorActual.cartas)[0].id
            # ultimojugador.Rol = "humano"
            commit()
            assert partida.finalizada == False
        client2.post(f'cartas/jugar?id_carta={idcarta}')
        assert(response.status_code == 200)
        # por ahora este json debe ser el de finalizar de partida ya que es el unico en jugar carta de ws,
        # desp si se agrega el de jugar carta, se cambia esto
        
        ####### Se queda esperando aca
        response = websocket.receive_json()
        #######
        assert response == {"event": "finalizar", "data": fin_partida_respond(partida.id).model_dump_json()}
        
        with db_session:
            assert Partida.get(id=partida.id).finalizada == True