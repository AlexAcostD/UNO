from flask import Flask,render_template,request,jsonify, session
from game.cartas import Carta, Color, Tipo
from game.engine import UNOGame
import uuid



##.\env\Scripts\activate
##python .\app\app.py
app=Flask(__name__)
app.secret_key = "CAMBIA_ESTO_POR_UNA_CLAVE_REALMENTE_SECRETA"
partida_actual = None



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/juego.html')
def juego_html():
    global partida_actual

    nombre = request.args.get('nombre')
    dificultad = request.args.get('dificultad')
    
    partida_actual = UNOGame(nombre_jugador=nombre, nombre_bot="Bot", cartas_por_jugador=7)
    
    manos = partida_actual.manos
    carta_inicial = partida_actual.carta_tope


    print("=== Carta Inicial ===")
    print(f"{carta_inicial.color.value} - {carta_inicial.tipo.value}" +
          (f" {carta_inicial.valor}" if carta_inicial.valor is not None else ""))
    
    print("==== MANO JUGADOR ====")
    for carta in manos[nombre]:
        print(f"  {carta.color.value} - {carta.tipo.value}" +
                (f" {carta.valor}" if carta.valor is not None else ""))
    print("==== MANO BOT ====")
    for carta in manos["Bot"]:
        print(f"  {carta.color.value} - {carta.tipo.value}" +
                (f" {carta.valor}" if carta.valor is not None else ""))
    

    
    return render_template('juego.html',nombre=nombre,
                            dificultad=dificultad,
                            mano_jugador=manos[nombre],
                            mano_bot=manos["Bot"],
                            carta_tope=carta_inicial,
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
    color = datos.get('color')
    tipo  = datos.get('tipo')
    valor = datos.get('valor') or None

    jugador = partida_actual.nombre_jugador

    # 1) Reconstruye y aplica la carta del jugador
    carta_jugada = Carta(
    Color(color),       # crea Color por valor, e.g. Color("AZUL")
    Tipo(tipo),         # crea Tipo por valor, e.g. Tipo("NUM")
    int(valor) if valor else None
    )
    try:
        partida_actual.jugar_carta(jugador, carta_jugada)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # 2) ¡Ahora es posible que sea el turno del bot!  
    #    Llamamos a la heurística del bot justo aquí:
    accion_bot = {}
    if partida_actual.turno == partida_actual.nombre_bot:
        accion_bot = partida_actual.turno_bot()

    # 3) Construimos la respuesta con TODO el estado y la acción del bot
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

if __name__ == '__main__':  
    app.run(debug=True ,port=5000)