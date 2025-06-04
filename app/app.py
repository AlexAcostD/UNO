from flask import Flask,render_template,request,jsonify
from game.engine import repartir_manos 
from game.cartas import Carta, Color, Tipo
from game.engine import UNOGame
import uuid



##.\env\Scripts\activate
##python .\app\app.py
app=Flask(__name__)
app.secret_key = "CAMBIA_ESTO_POR_UNA_CLAVE_REALMENTE_SECRETA"
PARTIDAS={}



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/juego.html')
def juego_html():
    nombre = request.args.get('nombre')
    dificultad = request.args.get('dificultad')
    
    partida = UNOGame(nombre_jugador=nombre, nombre_bot="Bot", cartas_por_jugador=7)
    
    manos = partida.manos
    carta_inicial = partida.carta_tope
  
  
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





if __name__ == '__main__':  
    app.run(debug=True ,port=5000)