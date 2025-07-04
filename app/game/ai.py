import random
import numpy as np
import os
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, InputLayer
from tensorflow.keras.optimizers import Adam
from enum import Enum

# ============================
# DEFINICIÓN DE CARTAS Y TIPOS
# ============================
class Tipo(Enum):
    NUMERO = 0
    PULSA_DOS = 1
    CAMBIA_COLOR = 2
    PIERDE_TURNO = 3

class Carta:
    def __init__(self, color, tipo, valor=None):
        self.color = color
        self.tipo = tipo
        self.valor = valor

    def __str__(self):
        return f"{self.color}_{self.tipo.name if self.tipo != Tipo.NUMERO else self.valor}"

    def to_id(self):
        return str(self)

# ============================
# GENERACIÓN DE CARTAS Y MAPEO
# ============================
def genCartas():
    COLORES = ['red', 'green', 'blue', 'yellow']
    VALORES = list(range(0, 10)) + [Tipo.PULSA_DOS, Tipo.PIERDE_TURNO, Tipo.CAMBIA_COLOR]

    TODAS_CARTAS = []
    for color in COLORES:
        for v in VALORES:
            if isinstance(v, int):
                TODAS_CARTAS.append(Carta(color, Tipo.NUMERO, v))
            else:
                TODAS_CARTAS.append(Carta(color, v))

    CARTA_TO_ID = {c.to_id(): i for i, c in enumerate(TODAS_CARTAS)}
    ID_TO_CARTA = {i: c for c, i in CARTA_TO_ID.items()}
    NUM_CARTAS = len(CARTA_TO_ID)

# ============================
# REGLAS DE COMPATIBILIDAD DE CARTAS
# ============================
def es_compatible(nueva: Carta, tope: Carta, acumulador_mas2: int = 0) -> bool:
    if acumulador_mas2 > 0:
        return nueva.tipo == Tipo.PULSA_DOS
    if nueva.tipo == Tipo.CAMBIA_COLOR:
        return True
    if nueva.tipo == Tipo.NUMERO and tope.tipo == Tipo.NUMERO:
        return nueva.color == tope.color or nueva.valor == tope.valor
    if nueva.tipo in (Tipo.PULSA_DOS, Tipo.PIERDE_TURNO):
        return nueva.color == tope.color or nueva.tipo == tope.tipo
    return nueva.color == tope.color

# ============================
# FILTRADO POR DIFICULTAD
# ============================
def filtrar_dificultad(mano, dificultad):
    if dificultad == 'facil':
        return [c for c in mano if c.tipo == Tipo.NUMERO or c.tipo == Tipo.CAMBIA_COLOR]
    elif dificultad == 'media':
        return [c for c in mano if c.tipo != Tipo.PIERDE_TURNO]
    else:  # dificil
        return mano

# ============================
# UTILIDADES DE CODIFICACIÓN
# ============================
def codificar_entrada(mano, carta_tope):
    entrada = np.zeros(NUM_CARTAS * 2)
    for c in mano:
        entrada[CARTA_TO_ID[c.to_id()]] = 1
    entrada[NUM_CARTAS + CARTA_TO_ID[carta_tope.to_id()]] = 1
    return entrada

def codificar_salida(carta):
    salida = np.zeros(NUM_CARTAS)
    salida[CARTA_TO_ID[carta.to_id()]] = 1
    return salida

# ============================
# GENERACIÓN DE DATOS DE ENTRENAMIENTO
# ============================
def generar_mano():
    return random.sample(TODAS_CARTAS, 7)

def generar_datos(n_samples=10000, dificultad='dificil'):
    X, y = [], []
    for _ in range(n_samples):
        tope = random.choice(TODAS_CARTAS)
        mano = generar_mano()
        mano_filtrada = filtrar_dificultad(mano, dificultad)
        jugables = [c for c in mano_filtrada if es_compatible(c, tope)]
        if not jugables:
            continue
        carta_elegida = random.choice(jugables)
        X.append(codificar_entrada(mano_filtrada, tope))
        y.append(codificar_salida(carta_elegida))
    return np.array(X), np.array(y)

def entrenar():
    MODEL_PATH = 'model_trained.keras'

    model = Sequential([
        InputLayer(input_shape=(NUM_CARTAS * 2,)),
        Dense(128, activation='relu'),
        Dense(64, activation='relu'),
        Dense(NUM_CARTAS, activation='softmax')
    ])
    model.compile(optimizer=Adam(0.001), loss='categorical_crossentropy', metrics=['accuracy'])

    # Entrenamiento para el nivel más difícil
    X_train, y_train = generar_datos(20000, dificultad='dificil')
    model.fit(X_train, y_train, epochs=8, batch_size=64)

    model.save(MODEL_PATH)

def cargar():
    MODEL_PATH = 'model_trained.keras'

    if os.path.exists(MODEL_PATH):
        model = load_model(MODEL_PATH)
    else:
        entrenar()

# ============================
# SELECCIÓN DE JUGADA POR LA IA
# ============================
def elegir_jugada(mano, carta_tope, dificultad='dificil'):
    mano_filtrada = filtrar_dificultad(mano, dificultad)
    entrada = codificar_entrada(mano_filtrada, carta_tope).reshape(1, -1)
    pred = model.predict(entrada, verbose=0)[0]
    indices = np.argsort(pred)[::-1]
    for idx in indices:
        carta_id = ID_TO_CARTA[idx]
        for carta in mano_filtrada:
            if carta.to_id() == carta_id and es_compatible(carta, carta_tope):
                return carta
    return None