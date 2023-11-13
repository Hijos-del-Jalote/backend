from api.api import app
from fastapi.testclient import TestClient
from pony.orm import db_session, commit
from db.models import Jugador,Carta, Partida, Rol
from db.cartas_session import carta_data
from unittest.mock import patch
import json
import datetime

def asignar_pos():
    with db_session:
        Jugador[1].Posicion = 1
        Jugador[1].Rol = Rol.lacosa
        commit()
        Jugador[2].Posicion = 2
        Jugador[2].Rol = Rol.humano
        Jugador[3].Posicion = 3
        Jugador[3].Rol = Rol.humano
        Jugador[4].Posicion = 4
        Jugador[4].Rol = Rol.humano
        commit()
        Jugador[1].partida.turnoActual=Jugador[1].id
        Jugador[1].partida.cantidadVivos = 4

def dar_cartas():
    with db_session:
        cartaj1 = Carta(id=1000,
                        template_carta = "Infectado",
                        jugador=Jugador[1],
                        partida=Partida[1])
        cartaj2 = Carta(id=1001,
                        template_carta = "Fallaste",
                        jugador=Jugador[2],
                        partida=Partida[1])
        cartaj3 = Carta(id=1002,
                        template_carta = "Lanzallamas",
                        jugador=Jugador[3],
                        partida=Partida[1])

def test_efecto_fallaste(setup_db_before_test, cleanup_db_after_test):
    
    client = TestClient(app)

    asignar_pos()
    dar_cartas()

    with client.websocket_connect("ws://localhost:8000/partidas/1/ws?idJugador=3") as websocket:
        with patch("api.ws.manager.get_from_message_queue") as mock_get_from_message_queue:
            mock_get_from_message_queue.side_effect = [json.dumps({"aceptado": False, "data": 1001}), 
                                                       json.dumps({"aceptado": True, "data": 1002})]
            response = client.put("/cartas/1000/intercambiar?idObjetivo=2")

        respws = websocket.receive_json()
        assert respws['event'] == "intercambio"
        assert respws['data'] == {'idJugador1': 1,
                                  'idJugador2': 2}

        respws = websocket.receive_json()
        assert respws['event'] == "intercambio_request"

        respws = websocket.receive_json()
        assert respws['event'] == "intercambio"
        assert respws['data'] == {'idJugador1': 1,
                                  'idJugador2': 3}

    with db_session:
        assert Carta[1000].jugador == Jugador[3]
        assert Carta[1001].jugador == None
        assert Carta[1002].jugador == Jugador[1]
        assert len(Jugador[2].cartas) == 1
        assert Jugador[3].Rol != Rol.infectado
        assert Jugador[2].Rol != Rol.infectado
        assert Partida[1].turnoActual == Jugador[2].id
        

