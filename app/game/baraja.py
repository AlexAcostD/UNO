
from game.cartas import Color,Tipo,Carta
import random
from typing import Optional, List

class Baraja:
    def __init__(self):
        self.cartas : List[Carta]=self.crear_baraja()
    def crear_baraja(self) -> List[Carta]:
        lista = []
        for color in Color:

            for num in range(1, 10):
                lista += [Carta(color, Tipo.NUMERO, num)] 
            for tipo in (Tipo.PULSA_DOS, Tipo.PIERDE_TURNO, Tipo.CAMBIA_COLOR):
                lista += [Carta(color, tipo)] 
                
        return lista
    
    def roba_carta(self) ->Carta:
        return self.cartas.pop(random.randrange(len(self.cartas)))
    def devolver_carta(self, carta: Carta) -> None:
        self.cartas.append(carta)
    
    
    