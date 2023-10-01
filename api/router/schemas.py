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
    jugadores: List[Dict[str, Union[str,int]]]
