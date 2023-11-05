from pony.orm import *
from enum import Enum
from db.settings import DATABASE_FILENAME


db = Database()

class Rol(str, Enum):
    lacosa = "La cosa"
    infectado = "Infectado"
    humano = "Humano"

class Tipo_Carta(str, Enum):
    panico = "Panico"
    accion = "Accion"
    defensa = "Defensa"
    obstaculo = "Obstaculo"
    contagio = "Contagio"

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
    partida = Optional('Partida')
    cartas = Set('Carta')


class Carta(db.Entity):
    id = PrimaryKey(int, auto=True)
    descartada = Required(bool, default=False)
    template_carta = Required('TemplateCarta')
    jugador = Optional(Jugador)
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
    finalizada = Optional(bool, default=False)
    jugadores = Set(Jugador)
    cantidadVivos = Optional(int)
    cartas = Set(Carta)
    ultimo_infectado = Optional(int)
    ultimaJugada = Optional(str, default = "")
    
# Conecta a la base de datos SQLite en el archivo 'database.sqlite'
db.bind(provider='sqlite', filename=DATABASE_FILENAME, create_db=True)

# Genera las tablas en la base de datos
db.generate_mapping(create_tables=True)
