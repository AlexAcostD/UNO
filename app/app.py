from flask import Flask,render_template,request,jsonify
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
    print(f"Jugador {jugador} ha tomado una carta.")
    print("=== MANO JUGADOR DESPUES DE TOMAR ===")
    for carta in partida_actual.manos[jugador]:
        print(f"  {carta.color.value} - {carta.tipo.value}" +
                (f" {carta.valor}" if carta.valor is not None else ""))
    
    
    return jsonify({
        'mano_jugador': [carta.to_dict() for carta in partida_actual.manos[jugador]],
        'cantidad_cartas_bot': len(partida_actual.manos[partida_actual.nombre_bot])
    })

if __name__ == '__main__':  
    app.run(debug=True ,port=5000)