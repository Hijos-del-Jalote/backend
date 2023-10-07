from pony.orm import *
from db.models import *
from db.cartas_session import *

CARTAS_POR_JUGADOR = {
    4 : {
        'infectado':8,
		'lanzallamas':2,
		'vacias':4,
        'sospecha':4,
        'seduccion':2,
        'mas vale que corras':2,
        'cambio de lugar':2,
        'analisis':0,
        'whisky':1,
        'hacha':1,
        'vigila tus espaldas':1,
        'determinacion':2,
        
	},
    5 : {
		'infectado':8,
		'lanzallamas':2,
		'vacias':9,
        'sospecha':4,
        'seduccion':2,
        'mas vale que corras':2,
        'cambio de lugar':2,
        'analisis':1,
        'whisky':1,
        'hacha':1,
        'vigila tus espaldas':1,
        'determinacion':2,
    },
    6 : {'infectado':10,
		'lanzallamas':3,
		'vacias':16,
        'sospecha':4,
        'seduccion':3,
        'mas vale que corras':2,
        'cambio de lugar':2,
        'analisis':2,
        'whisky':2,
        'hacha':1,
        'vigila tus espaldas':1,
        'determinacion':3,
    },
    7 : {'infectado':12,
		'lanzallamas':3,
		'vacias':19,
        'sospecha':5,
        'seduccion':4,
        'mas vale que corras':3,
        'cambio de lugar':3,
        'analisis':2,
        'whisky':2,
        'hacha':1,
        'vigila tus espaldas':1,
        'determinacion':3,
    },
    8 : {'infectado':13,
		'lanzallamas':3,
		'vacias':23,
        'sospecha':6,
        'seduccion':5,
        'mas vale que corras':3,
        'cambio de lugar':3,
        'analisis':2,
        'whisky':2,
        'hacha':1,
        'vigila tus espaldas':1,
        'determinacion':3,
    },
    9: {'infectado':15,
		'lanzallamas':4,
		'vacias':31,
        'sospecha':7,
        'seduccion':5,
        'mas vale que corras':4,
        'cambio de lugar':4,
        'analisis':3,
        'whisky':2,
        'hacha':2,
        'vigila tus espaldas':2,
        'determinacion':4,
    },
    10: {'infectado':17,
		'lanzallamas':4,
		'vacias':33,
        'sospecha':8,
        'seduccion':6,
        'mas vale que corras':4,
        'cambio de lugar':4,
        'analisis':3,
        'whisky':3,
        'hacha':2,
        'vigila tus espaldas':2,
        'determinacion':5,
    },
    11: {'infectado':20,
		'lanzallamas':5,
		'vacias':39,
        'sospecha':8,
        'seduccion':7,
        'mas vale que corras':5,
        'cambio de lugar':5,
        'analisis':3,
        'whisky':3,
        'hacha':2,
        'vigila tus espaldas':2,
        'determinacion':5,
    },
    12: {'infectado':20,
		'lanzallamas':5,
		'vacias':39,
        'sospecha':8,
        'seduccion':7,
        'mas vale que corras':5,
        'cambio de lugar':5,
        'analisis':3,
        'whisky':3,
        'hacha':2,
        'vigila tus espaldas':2,
        'determinacion':5,
    }
}


@db_session
def crear_mazo_jugadores(partida, cantidad_jug):
    crear_carta(TemplateCarta.get(nombre="La cosa"),partida)
    infectado= TemplateCarta.get(nombre="Infectado")
    sospecha= TemplateCarta.get(nombre="Sospecha")
    seduccion= TemplateCarta.get(nombre="Seduccion")
    mas_vale_que_corras= TemplateCarta.get(nombre="Mas vale que corras")
    cambio_de_lugar= TemplateCarta.get(nombre="Cambio de lugar")
    analisis= TemplateCarta.get(nombre="Analisis")
    whisky= TemplateCarta.get(nombre="Whisky")
    hacha= TemplateCarta.get(nombre="Hacha")
    vigila_tus_espaldas= TemplateCarta.get(nombre="Vigila tus espaldas")
    determinacion= TemplateCarta.get(nombre="Determinacion")
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    for _ in range(CARTAS_POR_JUGADOR[cantidad_jug]['lanzallamas']):
        crear_carta(lanzallamas,partida)
    for _ in range(CARTAS_POR_JUGADOR[cantidad_jug]['vacias']):
        crear_carta(cartavacia ,partida)
    for _ in range(CARTAS_POR_JUGADOR[cantidad_jug]['infectado']):
        crear_carta(infectado,partida)
    for _ in range(CARTAS_POR_JUGADOR[cantidad_jug]['sospecha']):
        crear_carta(sospecha,partida)
    for _ in range(CARTAS_POR_JUGADOR[cantidad_jug]['seduccion']):
        crear_carta(seduccion,partida)
    for _ in range(CARTAS_POR_JUGADOR[cantidad_jug]['mas vale que corras']):
        crear_carta(mas_vale_que_corras,partida)
    for _ in range(CARTAS_POR_JUGADOR[cantidad_jug]['cambio de lugar']):
        crear_carta(cambio_de_lugar,partida)
    for _ in range(CARTAS_POR_JUGADOR[cantidad_jug]['analisis']):
        crear_carta(analisis,partida)
    for _ in range(CARTAS_POR_JUGADOR[cantidad_jug]['whisky']):
        crear_carta(whisky,partida)
    for _ in range(CARTAS_POR_JUGADOR[cantidad_jug]['hacha']):
        crear_carta(hacha,partida)
    for _ in range(CARTAS_POR_JUGADOR[cantidad_jug]['vigila tus espaldas']):
        crear_carta(vigila_tus_espaldas,partida)
    for _ in range(CARTAS_POR_JUGADOR[cantidad_jug]['determinacion']):
        crear_carta(determinacion,partida)
    return 0


def crear_mazo(partida):
    num_jugadores = len(partida.jugadores)
    crear_mazo_jugadores(partida,num_jugadores)
    return 0    
        