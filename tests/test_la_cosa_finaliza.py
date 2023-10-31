from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from api.router.partidas import *
from db.models import *
from tests.test_newplayer import random_user
from db.cartas_session import *
from api.router.cartas import *
from api.ws import *
import asyncio


client = TestClient(app)


def test_la_cosa_finaliza_exceptions(cleanup_db_after_test):
    with db_session:
        partida = Partida(nombre="partida", iniciada=False, finalizada=False , maxJug=5, minJug=4)
        partida2 = Partida(nombre="partida", iniciada=True, finalizada=True , maxJug=5, minJug=4)
        db.commit()
        La_Cosa = Jugador(nombre="Jugador", Posicion=0, Rol="La cosa", isAlive=True, partida=partida)
        jugador2 = Jugador(nombre="Jugador", Posicion=0, Rol="Infectado", isAlive=True, partida=partida)
        jugador3 = Jugador(nombre="Jugador", Posicion=0, Rol="La cosa", isAlive=True, partida=partida2)
        db.commit()
        response= client.put(f'jugadores/{jugador2.id}/lacosafinaliza')  ### Un jugador que no es la cosa finaliza la partida
        assert response.status_code == 400
        response= client.put(f'jugadores/{La_Cosa.id}/lacosafinaliza')   ### Partida no iniciada
        assert response.status_code == 400 
        response = client.put(f'jugadores/{jugador3.id}/lacosafinaliza')  ### Partida ya finalizada
        assert response.status_code == 400
        response= client.put(f'jugadores/{9999}/lacosafinaliza')  ### No existe jugador con ese id
        assert response.status_code == 404

async def test_la_cosa_finaliza_pierde(cleanup_db_after_test):
    client1 = TestClient(app)
    with db_session:
        ganadores=[]
        partida = Partida(nombre="partida", iniciada=True, finalizada=False , maxJug=5, minJug=4)
        db.commit()
        La_Cosa = Jugador(nombre="Jugador", Posicion=0, Rol="La cosa", isAlive=True, partida=partida)
        jugador2 = Jugador(nombre="Jugador", Posicion=0, Rol="Humano", isAlive=True, partida=partida)
        jugador3 = Jugador(nombre="Jugador", Posicion=0, Rol="Humano", isAlive=True, partida=partida)
        db.commit()
        ganadores.append(jugador2.id)
        ganadores.append(jugador3.id)
        with client1.websocket_connect(f"ws://localhost:8000/partidas/{partida.id}/ws?idJugador={La_Cosa.id}") as websocket:
            while len(manager.active_connections.get(1, {})) != 1:
                await asyncio.sleep(0.1)
            assert len(manager.active_connections[1]) == 1
            response2= client.put(f'jugadores/{La_Cosa.id}/lacosafinaliza')
            assert response2.status_code == 200 
            response = websocket.receive_json()
            # {"event": "finalizar", "data": json.dumps({'isHumanoTeamWinner': True, 'winners': sorted(ganadores)})}
            assert response == {"event": "finalizar", "data": json.dumps({'isHumanoTeamWinner': True, 'winners': sorted(ganadores)},
                                            separators=(',',':'))}
    with db_session:
        jugador2 = Jugador.get(id=jugador2.id)
        La_Cosa = Jugador.get(id=La_Cosa.id)
        jugador3 = Jugador.get(id=jugador3.id)
        partida = Partida.get(id=partida.id)
        assert jugador2.partida==None
        assert La_Cosa.partida==None
        assert jugador3.partida==None
        assert partida.finalizada==True 
                
            
async def test_la_cosa_finaliza_gana(cleanup_db_after_test):
    client1 = TestClient(app)
    with db_session:
        ganadores=[]
        partida = Partida(nombre="partida", iniciada=True, finalizada=False , maxJug=5, minJug=4)
        db.commit()
        La_Cosa = Jugador(nombre="Jugador", Posicion=0, Rol="La cosa", isAlive=True, partida=partida)
        jugador2 = Jugador(nombre="Jugador", Posicion=0, Rol="infectado", isAlive=True, partida=partida)
        db.commit()
        ganadores.append(La_Cosa.id) 
        ganadores.append(jugador2.id)
        with client1.websocket_connect(f"ws://localhost:8000/partidas/{partida.id}/ws?idJugador={La_Cosa.id}") as websocket:
            while len(manager.active_connections.get(1, {})) != 1:
                await asyncio.sleep(0.1)
            assert len(manager.active_connections[1]) == 1
            response2= client.put(f'jugadores/{La_Cosa.id}/lacosafinaliza')
            assert response2.status_code == 200 
            response = websocket.receive_json()
            # {"event": "finalizar", "data": json.dumps({'isHumanoTeamWinner': True, 'winners': sorted(ganadores)})}
            assert response== {"event": "finalizar", "data": json.dumps({'isHumanoTeamWinner': False, 'winners': sorted(ganadores)},
                                            separators=(',',':'))}
    with db_session:
        jugador2 = Jugador.get(id=jugador2.id)
        La_Cosa = Jugador.get(id=La_Cosa.id)
        partida = Partida.get(id=partida.id)
        assert jugador2.partida==None
        assert La_Cosa.partida==None
        assert partida.finalizada==True 
        