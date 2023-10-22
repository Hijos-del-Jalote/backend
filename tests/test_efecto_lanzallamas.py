from fastapi.testclient import TestClient
from fastapi import status
from api.api import app
from api.router.cartas import *
from pony.orm import db_session
from db.models import *

client = TestClient(app)


def test_efecto_lanzallamas(cleanup_db_after_test):
    with db_session:
        l = False
        #Crear template de una carta lanzallamas si no existe
        if not TemplateCarta.exists(nombre="Lanzallamas"):
            template_carta = TemplateCarta(nombre="Lanzallamas", descripcion="Esta es una carta de prueba", tipo=Tipo_Carta.accion)
            l = True
        else:
            template_carta = TemplateCarta.get(nombre="Lanzallamas")
        #Crear un jugador que jugara la carta
        jugador1 = Jugador(nombre="Diego", isHost=True, isAlive=True, blockIzq=False, blockDer=False, Posicion=0)
        #Crear un jugador que recibira el efecto
        jugador2 = Jugador(nombre="Chun", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=1)
        #Crear una partida con jugadores
        partida = Partida(nombre="Partida", maxJug=5, minJug=1, sentido=False, iniciada=True, turnoActual=0, jugadores={jugador1, jugador2})
        #Crear carta y asignarsela al jugador1 y partida
        carta = Carta(descartada=False, template_carta=template_carta, partida=partida, jugador=jugador1)
        db.commit()
        #Jugar carta contra el jugador 2
        response = client.post(f'cartas/jugar?id_carta={carta.id}&id_objetivo={jugador2.id}&test=True')
        assert(response.status_code == 200)
        #Jugar carta sin pasar objetivo
        response = client.post(f'cartas/jugar?id_carta={carta.id}')
        assert(response.status_code == 400)
        #Jugar carta pasando objetivo inexistente
        response = client.post(f'cartas/jugar?id_carta={carta.id}&id_objetivo={10000000000}&test=True')
        assert(response.status_code == 400)
        
        if l:
            template_carta.delete()
        jugador1.delete()
        jugador2.delete()
        partida.delete()
        carta.delete()

