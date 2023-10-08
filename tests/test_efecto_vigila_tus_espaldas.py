from fastapi.testclient import TestClient
from fastapi import status
from api.api import app
from api.router.cartas import *
from pony.orm import db_session
from db.models import *

client = TestClient(app)

@db_session
def test_efecto_vigila_tus_espaldas():
    with db_session:
        l = False
        #Crear template de una carta vigila tus espaldas si no existe
        if not TemplateCarta.exists(nombre="Vigila tus espaldas"):
            template_carta = TemplateCarta(nombre="Vigila tus espaldas", descripcion="Esta es una carta de prueba", tipo=Tipo_Carta.accion)
            l = True
        else:
            template_carta = TemplateCarta.get(nombre="Vigila tus espaldas")
        #Crear un jugador que jugara la carta
        jugador1 = Jugador(nombre="Diego", isHost=True, isAlive=True, blockIzq=False, blockDer=False, Posicion=0)
        #Crear una partida con jugadores
        partida = Partida(nombre="Partida", maxJug=5, minJug=1, sentido=False, iniciada=True, turnoActual=0, jugadores={jugador1})
        #Crear carta y asignarsela al jugador1 y partida
        carta = Carta(descartada=False, template_carta=template_carta, partida=partida, jugador=jugador1)
        db.commit()
        #Jugar carta
        response = client.post(f'cartas/jugar?id_carta={carta.id}')
        assert(response.status_code == 200)
        #Pedir info de la partida cambiada
        response_partida = client.get(f'partidas/{partida.id}')
        #Checkear que se haya cambiado el sentido de la partida, deberia ser true
        assert(response_partida.json()["sentido"] == True)
        #Asignar la carta nuevamente
        carta = Carta(descartada=False, template_carta=template_carta, partida=partida, jugador=jugador1)
        db.commit()
        #Jugar carta nuevamente
        response = client.post(f'cartas/jugar?id_carta={carta.id}')
        assert(response.status_code == 200)
        #Pedir info de la partida cambiada
        response_partida = client.get(f'partidas/{partida.id}')
        #Ahora el sentido deberia ser False 
        assert(response_partida.json()["sentido"] == False)
        
        if l:
            template_carta.delete()
        jugador1.delete()
        partida.delete()
        carta.delete()

