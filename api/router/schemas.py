from pydantic import BaseModel
from typing import List, Optional, Dict, Union

class PlayerResponse(BaseModel):
    id: int

class PartidaIn(BaseModel):
    nombrePartida: str

class PartidaOut(BaseModel):
    idPartida: int

class EstadoPartida(BaseModel):
    finalizada: bool
    idGanador: int

class PartidaResponse(BaseModel):
    nombre: str
    maxJugadores: int
    minJugadores: int
    iniciada: bool
    turnoActual: Optional[int]
    sentido: bool
    jugadores: List[Dict[str, Union[str,Optional[int],bool,str]]]

class JugadorResponse(BaseModel):
    nombre: str
    isHost: Optional[bool]
    posicion: Optional[int]
    isAlive: Optional[bool]
    blockIzq: bool
    blockDer: bool
    cuarentena: bool
    cuarentenaCount: int
    rol: Optional[str]
    cartas: Optional[List[Dict[str,Union[str,int]]]]

class FinPartidaResponse(BaseModel):
    isHumanoTeamWinner: Optional[bool]
    winners: Optional[List[int]]

class JugarCartaData(BaseModel):
    idJugador: int
    idObjetivo: int
    idCarta: int
    template_carta: str
    nombreJugador: str
    nombreObjetivo: str
