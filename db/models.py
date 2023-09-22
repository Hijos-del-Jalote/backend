from pony.orm import *
from enum import Enum
from settings import DATABASE_FILENAME


db = Database()

class Rol(str, Enum):
    lacosa = "lacosa"
    infectado = "infectado"
    humano = "humano"

class Tipo_Carta(str, Enum):
    panico = "panico"
    accion = "accion"
    defensa = "defensa"
    obstaculo = "obstaculo"
    contagio = "contagio"

class Jugador(db.Entity):
    id = PrimaryKey(int, auto=True)
    nombre = Required(str)
    isHost = Required(bool, default=False)
    Posicion = Optional(int)
    Rol = Optional(Rol)
    isAlive = Required(bool, default=True)
    blockIzq = Required(bool, default=False)
    blockDer = Required(bool, default=False)
    cuarentena = Optional(bool, default=False)
    partida = Required('Partida')
    cartas = Set('Carta')


class Carta(db.Entity):
    id = PrimaryKey(int, auto=True)
    descartada = Required(bool, default=False)
    template_carta = Required('TemplateCarta')
    jugador = Required(Jugador)
    partida = Required('Partida')


class TemplateCarta(db.Entity):
    nombre = PrimaryKey(str, auto=True)
    descripcion = Optional(str)
    tipo = Optional(Tipo_Carta)
    cartas = Set(Carta)


class Partida(db.Entity):
    id = PrimaryKey(int, auto=True)
    nombre = Required(str)
    password = Optional(str, default='')
    maxJug = Required(int)
    minJug = Required(int)
    turnoActual = Optional(int)
    sentido = Required(bool, default=True)
    iniciada = Required(bool, default=False)
    jugadors = Set(Jugador)
    cartas = Set(Carta)


# Conecta a la base de datos SQLite en el archivo 'database.sqlite'
db.bind(provider='sqlite', filename=DATABASE_FILENAME, create_db=True)

# Genera las tablas en la base de datos
db.generate_mapping(create_tables=True)