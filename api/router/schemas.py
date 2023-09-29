from pydantic import BaseModel

class PlayerResponse(BaseModel):
    id: int

class PartidaIn(BaseModel):
    nombrePartida: str

class PartidaOut(BaseModel):
    idPartida: int

class EstadoPartida(BaseModel):
    finalizada: bool
    idGanador: int