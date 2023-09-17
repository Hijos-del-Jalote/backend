from backend.db.models import Partida, Jugador, Carta
from pony.orm import db_session
from typing import List

class Session: # revisar lo del nombre

    @db_session
    def crear_partida(self, id, nombre, password,
                        maxJug, minJug):
        Partida(id = id, nombre = nombre, password = password,
                maxJug = maxJug, minJug = minJug, turnoActual = 0,
                sentido = True, iniciada = False, jugadors = set(), 
                cartas = set())

    @db_session
    def get_partida(self, partida_id: int) -> dict:
        partida = Partida.get(id=partida_id)
        if partida is None:
            raise ValueError("Partida no existente")
        return {'id': partida_id, 'nombre': partida.nombre, 'password': partida.password,
            'maxJug': patida.maxJug, 'minJug': partida.minJug, 'turnoActual': partida.turnoActual,
            'sentido': partida.sentido, 'iniciada': partida.iniciada, 'jugadors': partida.jugadors,
            'cartas': partida.cartas}
        
    @db_session
    def get_partidas(self) -> List[dict]:
        partidas = [
            {'id': partida_id, 'nombre': partida.nombre, 'password': partida.password,
            'maxJug': patida.maxJug, 'minJug': partida.minJug, 'turnoActual': partida.turnoActual,
            'sentido': partida.sentido, 'iniciada': partida.iniciada, 'jugadors': partida.jugadors,
            'cartas': partida.cartas}
            for partida in Partida.select() 
        ]
        return partidas

