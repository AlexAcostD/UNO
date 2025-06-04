function iniciarJuego(nombre, dificultad) {
  fetch('/api/jugar', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ nombre, dificultad })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('resultado').textContent = data.resultado;
  })
  .catch(err => {
    console.error("Error al iniciar el juego:", err);
  });
}
