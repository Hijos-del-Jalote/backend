from api.api import app
from fastapi.testclient import TestClient
from pony.orm import db_session, commit
from db.models import Jugador,Partida
from api.ws import manager
import json
from typing import List
import asyncio
from unittest.mock import AsyncMock, patch

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

    response = client2.put(f"partidas/iniciar/{partida.id}")
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
    
    async def fake_get_from_message_queue(id_partida, id_objetivo):
        # Simular una respuesta que se esperaría
        response_data = {
            "defendido": False,
            "idCarta": 1  
        }
        return json.dumps(response_data)
        
    with client1.websocket_connect(f"ws://localhost:8000/partidas/{partida.id}/ws?idJugador={idlacosa}") as websocket:
        while len(manager.active_connections.get(partida.id, {})) != 1:
            await asyncio.sleep(0.1)

        with patch("api.ws.manager.get_from_message_queue", new_callable=AsyncMock) as mock_get_from_message_queue:
            mock_get_from_message_queue.side_effect = fake_get_from_message_queue
            response2 = client2.post(f'cartas/jugar?id_carta={idcarta}&id_objetivo={idlacosa}')

        assert(response2.status_code == 200)

        websocket.receive_json() #ignoro los dos primeros json que se mandan
        websocket.receive_json()
        response = websocket.receive_json()
        # {"event": "finalizar", "data": json.dumps({'isHumanoTeamWinner': True, 'winners': sorted(ganadores)})}
        assert response == {"event": "finalizar", "data": json.dumps({'isHumanoTeamWinner': True, 'winners': sorted(ganadores)},
                                         separators=(',',':'))}
        
        with db_session:
            assert Partida.get(id=partida.id).finalizada == True
            assert len(Partida.get(id=partida.id).jugadores)==0
            for c in Partida.get(id=partida.id).cartas:
                assert c.jugador == None