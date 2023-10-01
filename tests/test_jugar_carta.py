from fastapi.testclient import TestClient
from fastapi import status
from api.api import app
from api.router.cartas import *
from pony.orm import db_session
from db.models import *

client = TestClient(app)


def test_jugar_carta():
    with db_session:
        #Crear template de una carta
        template_carta = TemplateCarta(nombre="Prueba", descripcion="Esta es una carta de prueba", tipo=Tipo_Carta.accion)
        #Crear un jugador
        jugador = Jugador(nombre="Diego", isHost=True, isAlive=True, blockIzq=False, blockDer=True)
        #Crear una partida con jugador host
        partida = Partida(nombre="Partida", maxJug=5, minJug=1, sentido=0, iniciada=True, jugadores={jugador})
        #Crear carta y asignarsela al jugador y partida
        carta = Carta(descartada=False, template_carta=template_carta, partida=partida, jugador=jugador)
        db.commit()
        #Jugar carta
        response = client.post(f'cartas/jugar?id_carta={carta.id}')
        #Fijarse que la carta y el jugador no esten relacionados
        assert(response.status_code == 200)
        #Jugar la carta nuevamente -> deberia dar error ya que la carta no pertenece a ningun jugador.
        response = client.post(f'cartas/jugar?id_carta={carta.id}')
        assert(response.status_code == 400)
        #Jugar carta inexistente -> deberia dar error
        response = client.post('cartas/jugar?id_carta=1000000')
        assert(response.status_code == 400)
        
        template_carta.delete()
        db.commit()
