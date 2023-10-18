from api.api import app
from fastapi.testclient import TestClient
from pony.orm import db_session
from db.models import Jugador,Carta, Partida
from db.cartas_session import carta_data
from fastapi import WebSocket
import threading
import time

client = TestClient(app)
client1 = TestClient(app)
client2 = TestClient(app)

def asignar_pos():
    with db_session:
        Jugador[1].Posicion = 1
        Jugador[2].Posicion = 2
        Jugador[3].Posicion = 3
        Jugador[4].Posicion = 4

def dar_cartas():
    with db_session:
        cartaj1 = Carta(id=1000,
                        template_carta = "Lanzallamas",
                        jugador=Jugador[1],
                        partida=Partida[1])
        cartaj2 = Carta(id=1001,
                        template_carta = "Seduccion",
                        jugador=Jugador[2],
                        partida=Partida[1])
        


async def test_intercambiar_exitoso(setup_db_before_test):

    asignar_pos()
    dar_cartas()

    completion_event = threading.Event()

    response = {}
    flag = False
    def send_intercambio_request():
        nonlocal response
        nonlocal flag
        response = client2.put("/cartas/1000/intercambiar?idObjetivo=2")
        print("retorno la wea")
        flag = True
        completion_event.set()  # Marcar que la tarea ha terminado
        


    def receive_ws2_response():
        with client2.websocket_connect(f'ws://localhost:8000/partidas/1/ws?idJugador=2') as ws2:
            print("hilo2")
            ws_intercambio = ws2.receive_json()
            print(f"hilo2.receive:: {ws_intercambio}")
            assert ws_intercambio == {'event': "intercambio_request", 'data': carta_data(1000)}
            
            ws_intercambio2 = ws2.receive_json()
            print(f"hilo2.receive:: {ws_intercambio2}")
            assert ws_intercambio2 == {'event': "intercambio",'data': {'idJugador1': 1,'idJugador2': 2} }
            
            print("hilo2.sending")
            ws2.send_json({"aceptado": True, "data": 1001})
            print('hilo2.donesending')
            # nonlocal flag
            # while not flag:
            #     pass
            ws2.close 
        completion_event.set()  # Marcarque la tarea ha terminado
    
    # Crear dos hilos para ejecutar las tareas
    send_thread = threading.Thread(target=send_intercambio_request)
    receive_thread = threading.Thread(target=receive_ws2_response)
    
    # Iniciar los hilos
    send_thread.start()
    receive_thread.start()
    # Esperar a que ambos hilos completen su ejecución
    send_thread.join()
    receive_thread.join()
    print(response)


def test_intercambiar_fallido(cleanup_db_after_test):
    assert True