from typing import List, Dict, Optional
from game.cartas import Carta, Tipo, Color
from game.baraja import Baraja
from game.ai     import elegir_jugada
import random
from tensorflow.keras import Model
from game.ai import entrenar, cargar

modelo : Model = cargar()

class UNOGame:
    def __init__(
        self,
        nombre_jugador: str,
        nombre_bot: str = "Bot",
        cartas_por_jugador: int = 7,
        dificultad: str = "FACIL",
    ) -> None:
        self.nombre_jugador = nombre_jugador
        self.nombre_bot = nombre_bot
        self.dificultad = dificultad
        self.baraja = Baraja()

        # Repartir manos
        self.manos: Dict[str, List[Carta]] = {nombre_jugador: [], nombre_bot: []}
        for _ in range(cartas_por_jugador):
            self.manos[nombre_jugador].append(self.baraja.roba_carta())
            self.manos[nombre_bot].append(self.baraja.roba_carta())

        # Carta inicial
        self.descartadas: List[Carta] = []
        carta = self.baraja.roba_carta()
        while carta.tipo != Tipo.NUMERO:
            self.baraja.devolver_carta(carta)
            random.shuffle(self.baraja.cartas)
            carta = self.baraja.roba_carta()
        self.carta_tope: Carta = carta
        self.descartadas.append(carta)

        # Estado de turno y acumulador +2
        self.turno: str = nombre_jugador
        self.acumulador_mas2: int = 0

    def _cambiar_turno(self) -> None:
        self.turno = (
            self.nombre_bot
            if self.turno == self.nombre_jugador
            else self.nombre_jugador
        )

    def robar_carta(self, jugador: str, cantidad: int = 1) -> None:
        """Robar `cantidad` cartas, reconstruyendo el mazo si se vacía"""
        for _ in range(cantidad):
            if not self.baraja.cartas:
                full = Baraja().crear_baraja()
                used = (
                    self.descartadas
                    + [self.carta_tope]
                    + self.manos[self.nombre_jugador]
                    + self.manos[self.nombre_bot]
                )
                self.baraja.cartas = [c for c in full if c not in used]
                random.shuffle(self.baraja.cartas)
            carta = self.baraja.roba_carta()
            self.manos[jugador].append(carta)

    def tomar_carta(self, jugador: str) -> None:
        # Si hay acumulador, roba acumulado y pasa turno
        if self.acumulador_mas2 > 0:
            self.robar_carta(jugador, self.acumulador_mas2)
            self.acumulador_mas2 = 0
            self._cambiar_turno()
        else:
            self.robar_carta(jugador)
            self._cambiar_turno()

    def _es_compatible(self, nueva: Carta, tope: Carta) -> bool:
        # Si hay acumulador, sólo +2 es válido
        if self.acumulador_mas2 > 0:
            return nueva.tipo == Tipo.PULSA_DOS

        # Comodín cambia color siempre válido
        if nueva.tipo == Tipo.CAMBIA_COLOR:
            return True

        # Carta número: coincidir color o valor
        if nueva.tipo == Tipo.NUMERO and tope.tipo == Tipo.NUMERO:
            return nueva.color == tope.color or nueva.valor == tope.valor

        # Carta número: coincidir color
    
        # Cartas especiales (+2 o Skip): coincidir color o tipo
        if nueva.tipo in (Tipo.PULSA_DOS, Tipo.PIERDE_TURNO):
            return nueva.color == tope.color or nueva.tipo == tope.tipo

        if nueva.color == tope.color:
            return True
        return False

    def _resolver_acumulador(self) -> None:
        if self.acumulador_mas2 == 0:
            return
        jugador = self.turno
        if any(c.tipo == Tipo.PULSA_DOS for c in self.manos[jugador]):
            return
        self.robar_carta(jugador, self.acumulador_mas2)
        self.acumulador_mas2 = 0
        self._cambiar_turno()

    def jugar_carta(
        self,
        jugador: str,
        carta: Carta,
        nuevo_color: Optional[str] = None
    ) -> None:
        
       
        # 1. Buscar la carta original exacta en la mano

        if carta.tipo == Tipo.CAMBIA_COLOR:
            encontrada = next((c for c in self.manos[jugador] if c.tipo == Tipo.CAMBIA_COLOR), None)
        else:
            encontrada = next((c for c in self.manos[jugador] if c == carta), None)

        if not encontrada:
            raise ValueError(f"No tienes la carta {carta} en tu mano.")
    # 2. Si es CCOLOR, actualizar su color con el nuevo_color
        if carta.tipo == Tipo.CAMBIA_COLOR:
            if not nuevo_color:
                raise ValueError("Debes especificar un nuevo color para una carta Cambia Color.")
            try:
                carta.color = Color(nuevo_color.upper())
            except ValueError:
                raise ValueError(f"Color inválido: {nuevo_color}")

        if not self._es_compatible(carta, self.carta_tope):
            raise ValueError("Carta no válida sobre la tope.")

        # 2. Remover carta original de la mano
        self.manos[jugador].remove(carta)
        self.descartadas.append(carta)
        self.carta_tope = carta

        # 5. Aplicar efectos si corresponde
        if carta.tipo == Tipo.PIERDE_TURNO:
            return
        if carta.tipo == Tipo.PULSA_DOS:
            self.acumulador_mas2 += 2
            self._cambiar_turno()
            return

        # 6. Cambio de turno estándar
        self._cambiar_turno()


    def turno_bot(self) -> Dict:
        bot = self.nombre_bot
        if self.acumulador_mas2 > 0:
            for c in list(self.manos[bot]):
                if c.tipo == Tipo.PULSA_DOS:
                    self.jugar_carta(bot, c)
                    return {"accion": "jugó", "carta": c.to_dict()}
                
            cantidad = self.acumulador_mas2
            self.robar_carta(bot, cantidad)
            self.acumulador_mas2 = 0
            self._cambiar_turno()
            return {"accion": "robó_acumulado", "cantidad": cantidad}

        for c in list(self.manos[bot]):
            if self._es_compatible(c, self.carta_tope):
                if c.tipo == Tipo.CAMBIA_COLOR:
                    # Mantener el mismo color de la carta tope
                    color_actual = self.carta_tope.color.name
                    self.jugar_carta(bot, c, nuevo_color=color_actual)
                else:
                    self.jugar_carta(bot, c)
                return {"accion": "jugó", "carta": c.to_dict()}

        self.robar_carta(bot)
        carta_robada = self.manos[bot][-1]
        if self._es_compatible(carta_robada, self.carta_tope):
            if carta_robada.tipo == Tipo.CAMBIA_COLOR:
                color_actual = self.carta_tope.color.name
                self.jugar_carta(bot, carta_robada, nuevo_color=color_actual)
            else:
                self.jugar_carta(bot, carta_robada)
            return {"accion": "robó_y_jugó", "carta": carta_robada.to_dict()}

        self._cambiar_turno()

        #response = elegir_jugada()
        #print(response)
        return {"accion": "robó", "carta": None}

    def estado_para_cliente(self) -> Dict:
        return {
            "mano_jugador": [c.to_dict() for c in self.manos[self.nombre_jugador]],
            "cantidad_cartas_bot": len(self.manos[self.nombre_bot]),
            "carta_tope": self.carta_tope.to_dict(),
            "turno": self.turno,    
        }
