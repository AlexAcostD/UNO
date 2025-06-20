from typing import List, Dict,Tuple,Optional
from game.cartas import Carta, Tipo, Color
from game.baraja import Baraja
import random



class UNOGame:
    def __init__(self, nombre_jugador: str, nombre_bot: str = "Bot", cartas_por_jugador: int = 7):
 
        self.nombre_jugador = nombre_jugador
        self.nombre_bot = nombre_bot
        self.baraja = Baraja()  
        
        self.manos: Dict[str, List[Carta]] = {
            nombre_jugador: [],
            nombre_bot: []
        }
        for _ in range(cartas_por_jugador):
            self.manos[nombre_jugador].append(self.baraja.roba_carta())
            self.manos[nombre_bot].append(self.baraja.roba_carta())

        self.descartadas: List[Carta] = []
        carta = self.baraja.roba_carta()
        # Repetir hasta que sea NUMERO (para que el juego arranque con una carta numérica)
        while carta.tipo != Tipo.NUMERO:
            self.baraja.devolver_carta(carta)
            random.shuffle(self.baraja.cartas)
            carta = self.baraja.roba_carta()
        self.carta_tope: Carta = carta
        self.descartadas.append(carta)

        # 4. Estado inicial de turno y acumulador de “+2”
        self.turno: str = nombre_jugador  # el jugador humano arranca
        self.acumulador_mas2: int = 0     # si alguien lanza +2, el siguiente roba acumulado
    def tomar_carta(self,jugador:str) -> None:
        if self.baraja.cartas:
            carta = self.baraja.roba_carta()
            self.manos[jugador].append(carta)
        else:
            print("No hay más cartas en la baraja para robar.")
    def jugar_carta(self, jugador, carta) :
        if not self._es_compatible(carta, self.carta_tope):
            raise ValueError("La carta no es compatible con la carta tope.")
    
        self.manos[jugador].remove(carta)
        self.descartadas.append(self.carta_tope)
        self.carta_tope = carta
        self.turno = self.nombre_bot if jugador == self.nombre_jugador else self.nombre_jugador
    def turno_bot(self):
        mano_bot=self.manos[self.nombre_bot]
        carta_jugada = None
        for carta in mano_bot:
            if self._es_compatible(carta, self.carta_tope):
                carta_jugada = carta
                break
        if carta_jugada:
            self.jugar_carta(self.nombre_bot, carta_jugada)
        else:
            self.tomar_carta(self.nombre_bot)
            
    def estado_para_cliente(self):
        return {
            "mano_jugador": [c.to_dict() for c in self.manos[self.nombre_jugador]],
            "cantidad_cartas_bot": len(self.manos[self.nombre_bot]),
            "carta_tope": self.carta_tope.to_dict(),
            "turno": self.turno
        }

    def _es_compatible(self, nueva, tope):
        if nueva.tipo == Tipo.CAMBIA_COLOR:
            return True
        if nueva.tipo == Tipo.NUMERO and tope.tipo == Tipo.NUMERO:
            return nueva.color == tope.color or nueva.valor == tope.valor
        return nueva.color == tope.color