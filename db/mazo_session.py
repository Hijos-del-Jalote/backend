from pony.orm import *
from db.models import *
from db.cartas_session import *

CARTAS_POR_JUGADOR = {
    4 : {
		'lanzallamas':2,
		'vacias':31
	},
    5 : {
		'lanzallamas':2,
		'vacias':31
    },
    6 : {'lanzallamas':3,
        'vacias':31
    },
    7 : {'lanzallamas':3,
        'vacias':55
    },
    8 : {'lanzallamas':4,
        'vacias':59
    },
    9: {'lanzallamas':4,
        'vacias':63
    },
    10: {'lanzallamas':4,
        'vacias':63
    },
    11: {'lanzallamas':5,
        'vacias':79
    },
    12: {'lanzallamas':5,
        'vacias':79
    }
}


@db_session
def crear_mazo_jugadores(partida, cantidad_jug):
    n_lanzallamas = CARTAS_POR_JUGADOR[cantidad_jug]['lanzallamas']
    n_vacias = CARTAS_POR_JUGADOR[cantidad_jug]['vacias']
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    crear_carta(TemplateCarta.get(nombre="La cosa"),partida)
    for _ in range(n_lanzallamas):
        crear_carta(lanzallamas,partida)
    for _ in range(n_vacias):
        crear_carta(cartavacia ,partida)
    return 0


def crear_mazo(partida):
    num_jugadores = len(partida.jugadores)
    crear_mazo_jugadores(partida,num_jugadores)
    return 0    
        