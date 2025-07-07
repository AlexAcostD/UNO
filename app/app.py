from flask import Flask,render_template,request,jsonify, session
from game.cartas import Carta, Color, Tipo
from game.engine import UNOGame
import game.ai
import psycopg2
import random

##.\env\Scripts\activate
##python .\app\app.py
app=Flask(__name__)
app.secret_key = "CAMBIA_ESTO_POR_UNA_CLAVE_REALMENTE_SECRETA"
partida_actual = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cargar.html')
def cargar_html():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="UNO",
        user="Alex",
        connect_timeout=10
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            p.id,
            p.carta_inicial_color,
            p.carta_inicial_tipo,
            p.carta_inicial_valor,
            p.dificultad,
            cm.jugador,
            array_agg(cm.color || '-' || cm.tipo || COALESCE('-' || cm.valor::text, '')) AS cartas_jugador
        FROM partidas p
        JOIN (
            SELECT id_partida, jugador, color, tipo, valor
            FROM cartas_en_mano
            WHERE jugador != 'Bot'
        ) cm ON p.id = cm.id_partida
        GROUP BY p.id, p.carta_inicial_color, p.carta_inicial_tipo, p.carta_inicial_valor, p.dificultad, cm.jugador
        ORDER BY p.id DESC
    """)
    partidas = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('cargar.html', partidas=partidas)

@app.route('/juego.html')
def juego_html():
    global partida_actual
    id_partida = request.args.get('id_partida')
    nombre = request.args.get('nombre')
    dificultad = request.args.get('dificultad')

    if id_partida:
        # Cargar partida desde la base de datos
        partida_actual = cargar_partida_desde_db(id_partida)
        if not partida_actual:
            return "Partida no encontrada o incompleta", 404
        nombre = partida_actual.nombre_jugador
        dificultad = partida_actual.dificultad
    elif nombre and dificultad:
        # Crear nueva partida
        partida_actual = UNOGame(nombre_jugador=nombre, nombre_bot="Bot", cartas_por_jugador=7, loadedModel=game.ai.cargar())
        partida_actual.dificultad = dificultad
        guardar_partida_en_db(partida_actual, dificultad)
    else:
        return "Faltan parámetros", 400
    print("=== MANO JUGADOR ===")
    for carta in partida_actual.manos[partida_actual.nombre_jugador]:
        print(f"  {carta.color.value} - {carta.tipo.value}" +
                (f" {carta.valor}" if carta.valor is not None else ""))
    print("=== MANO BOT ===")
    for carta in partida_actual.manos[partida_actual.nombre_bot]:
        print(f"  {carta.color.value} - {carta.tipo.value}" +
                (f" {carta.valor}" if carta.valor is not None else ""))
    print(f"carta_tope: {partida_actual.carta_tope.color.value} - {partida_actual.carta_tope.tipo.value}" +
            (f" {partida_actual.carta_tope.valor}" if partida_actual.carta_tope.valor is not None else ""))
    return render_template(
        'juego.html',
        nombre=partida_actual.nombre_jugador,
        dificultad=partida_actual.dificultad,
        mano_jugador=partida_actual.manos[partida_actual.nombre_jugador],
        mano_bot=partida_actual.manos[partida_actual.nombre_bot],
        carta_tope=partida_actual.carta_tope,
        Tipo=Tipo
    )

@app.route('/tomar', methods=['POST'])
def tomar_carta():
    global partida_actual
    jugador=partida_actual.nombre_jugador
    partida_actual.tomar_carta(jugador)
    ##turno del bot

    accion_bot = partida_actual.turno_bot()
    print("=== MANO BOT DESPUES DE TOMAR ===")
    for carta in partida_actual.manos[partida_actual.nombre_bot]:
        print(f"  {carta.color.value} - {carta.tipo.value}" +
                (f" {carta.valor}" if carta.valor is not None else ""))
    
    print(f"Jugador {jugador} ha tomado una carta.")
    print("=== MANO JUGADOR DESPUES DE TOMAR ===")
    for carta in partida_actual.manos[jugador]:
        print(f"  {carta.color.value} - {carta.tipo.value}" +
                (f" {carta.valor}" if carta.valor is not None else ""))
    
    print(f"carta_tope: {partida_actual.carta_tope.color.value} - {partida_actual.carta_tope.tipo.value}" +
            (f" {partida_actual.carta_tope.valor}" if partida_actual.carta_tope.valor is not None else ""))
    return jsonify({
        'mano_jugador': [c.to_dict() for c in partida_actual.manos[jugador]],
        'carta_tope': partida_actual.carta_tope.to_dict(),
        'cantidad_cartas_bot': len(partida_actual.manos[partida_actual.nombre_bot]),
        'accion_bot': accion_bot
    })
    
@app.route('/jugar', methods=['POST'])
def jugar_carta():
    global partida_actual
    datos = request.get_json()
    
    print("DEBUG datos:", datos)
    nuevo_color = datos.get("nuevo_color")
    print("DEBUG nuevo_color:", nuevo_color)

    color = datos.get('color')
    tipo  = datos.get('tipo')
    valor = datos.get('valor') or None
    jugador = partida_actual.nombre_jugador

    tipo_enum = Tipo(tipo)
    valor_int = int(valor) if valor else None

    # 🟨 CASO ESPECIAL: CCOLOR
    if tipo_enum == Tipo.CAMBIA_COLOR:
        if not nuevo_color:
            return jsonify({'error': 'Debes especificar un nuevo color para una carta Cambia Color.'}), 400
        try:
            color_enum = Color(nuevo_color.upper())
        except ValueError:
            return jsonify({'error': f"Color inválido: {nuevo_color}"}), 400

        carta_jugada = Carta(color=color_enum, tipo=tipo_enum, valor=valor_int)
    else:
        carta_jugada = Carta(color=Color(color), tipo=tipo_enum, valor=valor_int)

    # ✅ Buscar carta real en la mano
    if carta_jugada.tipo == Tipo.CAMBIA_COLOR:
        encontrada = next((c for c in partida_actual.manos[jugador] if c.tipo == Tipo.CAMBIA_COLOR), None)
    else:
        encontrada = next((c for c in partida_actual.manos[jugador] if c == carta_jugada), None)

    if not encontrada:
        return jsonify({'error': f"No tienes la carta {carta_jugada} en tu mano."}), 400

    # ✅ Aplicar jugada
    try:
        partida_actual.manos[jugador].remove(encontrada)
        partida_actual.descartadas.append(carta_jugada)
        partida_actual.carta_tope = carta_jugada
        partida_actual._cambiar_turno()
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # 🤖 Acción del bot si le toca
    accion_bot = {}
    if partida_actual.turno == partida_actual.nombre_bot:
        accion_bot = partida_actual.turno_bot()

    estado = partida_actual.estado_para_cliente()
    estado['accion_bot'] = accion_bot



    for carta in partida_actual.manos[jugador]:
        print(f"  {carta.color.value} - {carta.tipo.value}" +
                (f" {carta.valor}" if carta.valor is not None else ""))
    print("bot ha jugado:")
    for carta in partida_actual.manos[partida_actual.nombre_bot]:
        print(f"  {carta.color.value} - {carta.tipo.value}" +
                (f" {carta.valor}" if carta.valor is not None else ""))
    print(f"carta_tope: {partida_actual.carta_tope.color.value} - {partida_actual.carta_tope.tipo.value}" +
            (f" {partida_actual.carta_tope.valor}" if partida_actual.carta_tope.valor is not None else ""))
    return jsonify(estado)


def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="UNO",
        user="Alex",            # tu usuario de PostgreSQL
        connect_timeout=10
    )
    return conn

@app.route('/guardar', methods=['POST'])
def  guardar_partida():
    global partida_actual
    if partida_actual is None:
        return jsonify({"ok": False, "error": "No hay partida en curso"}), 400

    try:
        guardar_partida_en_db(partida_actual, partida_actual.dificultad)
        print("✅ Partida guardada desde /guardar")
        return jsonify({"ok": True})
    except Exception as e:
        print(f"❌ Error guardando partida: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500
    
def guardar_partida_en_db(partida,dificultad):
    id_partida = random.randint(10000, 99999)
    print("ID generada:", id_partida)

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="UNO",
        user="Alex",
        connect_timeout=10
    )
    cur = conn.cursor()
    
    carta = partida.carta_tope
    # ✅ Agregado dificultad en INSERT
    cur.execute("""
        INSERT INTO partidas (id, carta_inicial_color, carta_inicial_tipo, carta_inicial_valor, dificultad)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        id_partida,
        carta.color.value,
        carta.tipo.value,
        carta.valor if carta.valor is not None else None,
        partida.dificultad  # ✅ Nueva columna dificultad
    ))
    
    # 4. Insertar las cartas en mano de ambos jugadores
    for jugador in [partida.nombre_jugador, partida.nombre_bot]:
        for carta in partida.manos[jugador]:
            cur.execute("""
                INSERT INTO cartas_en_mano (id_partida, jugador, color, tipo, valor)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                id_partida,
                jugador,
                carta.color.value,
                carta.tipo.value,
                carta.valor if carta.valor is not None else None
            ))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Partida y cartas guardadas exitosamente en la base de datos.")

def cargar_partida_desde_db(id_partida):
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="UNO",
        user="Alex"
    )
    cur = conn.cursor()

    cur.execute("SELECT carta_inicial_color, carta_inicial_tipo, carta_inicial_valor, dificultad FROM partidas WHERE id = %s", (id_partida,))
    fila = cur.fetchone()
    if not fila:
        return None

    carta_inicial = Carta(Color(fila[0]), Tipo(fila[1]), fila[2])
    dificultad = fila[3]

    cur.execute("SELECT jugador, color, tipo, valor FROM cartas_en_mano WHERE id_partida = %s", (id_partida,))
    cartas_filas = cur.fetchall()

    jugadores = set(row[0] for row in cartas_filas)
    if "Bot" not in jugadores or len(jugadores) != 2:
        return None

    jugador_humano = next(j for j in jugadores if j != "Bot")
    partida = UNOGame(jugador_humano, "Bot")
    partida.carta_tope = carta_inicial
    partida.dificultad = dificultad
    partida.manos = {j: [] for j in jugadores}

    for jugador, color, tipo, valor in cartas_filas:
        carta = Carta(Color(color), Tipo(tipo), valor)
        partida.manos[jugador].append(carta)

    cur.close()
    conn.close()
    return partida





if __name__ == '__main__':  
    app.run(debug=True ,port=5000)