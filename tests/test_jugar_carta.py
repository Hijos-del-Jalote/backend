from fastapi.testclient import TestClient
from fastapi import status
from api.api import app
from api.router.cartas import *
from pony.orm import db_session
from db.models import *

client = TestClient(app)


def test_jugar_carta():
    with db_session:
        l = False
        #Crear template de una carta
        if not TemplateCarta.exists(nombre="Prueba"):
            template_carta = TemplateCarta(nombre="Prueba", descripcion="Esta es una carta de prueba", tipo=Tipo_Carta.accion)
            l = True
        else:
            template_carta = TemplateCarta.get(nombre="Prueba")
        #Crear un jugador
        jugador = Jugador(nombre="Diego", isHost=True, isAlive=True, blockIzq=False, blockDer=True, Posicion=1)
        #Crear una partida con jugador host
        partida = Partida(nombre="Partida", maxJug=5, minJug=1, iniciada=True, turnoActual=0, sentido = False, jugadores={jugador})
        #Crear carta y asignarsela al jugador y partida
        carta = Carta(descartada=False, template_carta=template_carta, partida=partida, jugador=jugador)
        db.commit()
        #Jugar carta, Deberia dar error ya que no es el turno del jugador
        response = client.post(f'cartas/jugar?id_carta={carta.id}')
        assert(response.status_code == 400)
        jugador.Posicion=0
        db.commit()
        
        turno = partida.turnoActual

        #El jugador deberia jugar la carta correctamente
        response = client.post(f'cartas/jugar?id_carta={carta.id}')
        assert(response.status_code == 200)

        assert partida.turnoActual == (turno - 1) % len(partida.jugadores)
        
        #Jugar la carta nuevamente -> deberia dar error ya que la carta no pertenece a ningun jugador.
        response = client.post(f'cartas/jugar?id_carta={carta.id}')
        assert(response.status_code == 400)
        #Jugar carta inexistente -> deberia dar error
        response = client.post('cartas/jugar?id_carta=1000000')
        assert(response.status_code == 400)
        if l:
            template_carta.delete()
        jugador.delete()
        partida.delete()
        carta.delete()
