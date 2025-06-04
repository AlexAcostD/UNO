from typing import List
from Cartas import Carta
import Baraja

class Masoo:
    def __init__(self, name: str, baraja: Baraja):
        self.name = name
        self.baraja = baraja
        self.cartas: List[Carta] = []
        self.anhadir(7)

    def extraer_carta(self) -> Carta:
        carta = self.baraja.roba_carta()
        self.cartas.append(carta)
        return carta

    def anhadir(self, cantidad: int):
        for _ in range(cantidad):
            self.extraer_carta()
            
    def jugar_carta(self, carta: Carta):
        if carta in self.cartas:
            self.cartas.remove(carta)
        else:
            print("No tienes esa carta en tu mano")
    def tamano(self) -> int:
        return len(self.cartas)
    

            
if __name__ == "__main__":  
    baraja = Baraja.Baraja()  
    mano_jugador = Masoo("Alexander",baraja)
    print("Cartas")
    for carta in baraja.cartas:
        print(carta.color, "-", carta.tipo, "-", carta.valor)
    
    print("Cartas del jugador:")   
    for carta in mano_jugador.cartas:
        print(carta.color, "-", carta.tipo, "-", carta.valor)