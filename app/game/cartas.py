import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

class Color(Enum):
    AZUL = "AZUL"
    VERDE = "VERDE"
    ROJO = "ROJO"
    AMARILLO = "AMARILLO"


class Tipo(Enum):
    NUMERO         = "NUM"
    PULSA_DOS      = "MAS2"
    PIERDE_TURNO   = "SKIP"
    CAMBIA_COLOR   = "CCOLOR"


@dataclass
class Carta:
    color: Color
    tipo: Tipo
    valor: Optional[int] = None  
    
    def to_dict(self) -> dict:
        # Construir string para el nombre de la imagen:
        # Si es carta numérica: "ROJO_5", "AZUL_9", etc.
        # Si es +2:       "VERDE_MAS2"
        # Si es Skip:     "AMARILLO_SKIP"
        # Si es CCOLOR:   "CAMBIA_COLOR" (sin color, porque siempre es comodín)
        if self.tipo == Tipo.NUMERO:
            rep = f"{self.color.value}_{self.valor}"
        elif self.tipo == Tipo.PULSA_DOS:
            rep = f"{self.color.value}_MAS2"
        elif self.tipo == Tipo.PIERDE_TURNO:
            rep = f"{self.color.value}_SKIP"
        elif self.tipo == Tipo.CAMBIA_COLOR:
            rep = "CCOLOR"
        else:
            rep = "DESCONOCIDA"  # no debería llegar aquí

        return {
            "color": self.color.value if self.color else None,
            "tipo": self.tipo.value,
            "valor": self.valor if self.valor is not None else None,
            "representacion": rep
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Carta":
        """
        Reconstruye una instancia Carta a partir de un diccionario con
        las mismas claves que genera to_dict(). Se asume que 'data["color"]'
        es uno de los strings de Color.value, y 'data["tipo"]' uno de Tipo.value.
        """
        col = Color(data["color"])
        tip = Tipo(data["tipo"] )
        val = data.get("valor", None)
        return cls(color=col, tipo=tip, valor=val)

    def __eq__(self, other):
        if not isinstance(other, Carta):
            return False
        return self.color == other.color and self.tipo == other.tipo and self.valor == other.valor

    def __hash__(self):
        return hash((self.color, self.tipo, self.valor))