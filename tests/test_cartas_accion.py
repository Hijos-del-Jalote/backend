from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from api.router.partidas import *
from db.models import *
from tests.test_newplayer import random_user
from db.mazo_session import *
from db.cartas_session import *

client = TestClient(app)

def populate_and_setup():
    jugadores = []
    for j in range(4):
        username = random_user()
        response = client.post(f'jugadores?nombre={username}')
        with db_session:
            jugadores.append(Jugador.get(id = response.json()["id"]))
    partida = random_user()
    host = jugadores[0]
    # creo partida
    response = client.post(f'partidas/?nombrePartida={partida}&idHost={host.id}') 
    with db_session:
        partida = Partida.get(id = response.json()["idPartida"])
    # uno jugadores a partida
    for i in range(1,4):
        client.post(f"partidas/unir?idPartida={partida.id}&idJugador={jugadores[i].id}")
    # inicio  partida
    response = client.put(f"partidas/iniciar/{partida.id}?idJugador={host.id}")    
    return partida
    
def test_cartas_accion(cleanup_db_after_test):
        partida = populate_and_setup()
        # verifico que haya la cant de cartas correcta
        with db_session:
            partida = Partida.get(id = partida.id)
            templates = list(TemplateCarta.select())
            assert templates[0].nombre == "La cosa" and templates[0].tipo == Tipo_Carta.contagio and templates[0].descripcion == "Te convertiste en la cosa pa"
            assert templates[1].nombre == "Lanzallamas" and templates[1].tipo == Tipo_Carta.accion and templates[1].descripcion == "matar a un jugador"
            assert templates[2].nombre == "Vigila tus espaldas" and templates[2].tipo == Tipo_Carta.accion and templates[2].descripcion == "Invierte el orden de la partida"
            assert templates[3].nombre == "Cambio de lugar" and templates[3].tipo == Tipo_Carta.accion and templates[3].descripcion == "Cambia de sitio con un jugador adyacente que no este en cuarentena o tras una puerta cerrada"
            assert templates[4].nombre == "Mas vale que corras" and templates[4].tipo == Tipo_Carta.accion and templates[4].descripcion == "Cambia de sitio con cualquier jugador  que no este en cuarentena ignora puertas trancadas"
            assert templates[5].nombre == "Seduccion" and templates[5].tipo == Tipo_Carta.accion and templates[5].descripcion == "Intercambia carta con cualquier jugador que no este en cuarentena , termina tu turno"
            assert templates[6].nombre == "Analisis" and templates[6].tipo == Tipo_Carta.accion and templates[6].descripcion == "Mira la mano de cartas de un jugador adyacente"
            assert templates[7].nombre == "Sospecha" and templates[7].tipo == Tipo_Carta.accion and templates[7].descripcion == "Mira una carta aleatoria de la mano de cartas de un jugador adyacente"
            assert templates[8].nombre == "Whisky" and templates[8].tipo == Tipo_Carta.accion and templates[8].descripcion == "Muestra todas tus cartas a todos los jugadores"
            assert templates[9].nombre == "Hacha" and templates[9].tipo == Tipo_Carta.accion and templates[9].descripcion == "retira una carta 'puerta atrancada' o 'cuarentena'sobre ti o un jugador adyacente"
            assert templates[10].nombre == "Determinacion" and templates[10].tipo == Tipo_Carta.accion and templates[10].descripcion == "roba 3 cartas 'Alejate',elige 1 para quedartela y descarta las demas , luego juega o descarta una carta"
            assert templates[11].nombre == "Infectado" and templates[11].tipo == Tipo_Carta.contagio and templates[11].descripcion == "Te convertiste en un infectado"
            
