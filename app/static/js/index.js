    function jugar() {
    const nombre = document.getElementById('nombre').value.trim();
    const dificultad = document.getElementById('btnDificultad').textContent;
    
    if (nombre.trim() === "") {
        alert("Por favor ingresa tu nombre.");
    } else {
    const nombreCodificado = encodeURIComponent(nombre);
    const dificultadCodificada = encodeURIComponent(dificultad);
    window.location.href = `juego.html?nombre=${nombreCodificado}&dificultad=${dificultadCodificada}`;
    }
    }


const niveles = ["FACIL", "MEDIO", "DIFICIL"];
let indiceDificultad = 0;


    function cambiarDificultad() {
    indiceDificultad = (indiceDificultad + 1) % niveles.length;
    const btn = document.getElementById('btnDificultad');
    btn.textContent = niveles[indiceDificultad];  
    }