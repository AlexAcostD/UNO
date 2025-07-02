// 1) Función para dispersar las cartas en abanico
function actualizarCartas(container) {
  const cards = container.querySelectorAll('img');
  const count = cards.length;
  const spread = 150;
  const step = count > 1 ? spread / (count - 1) : 0;

  cards.forEach((card, i) => {
    const angle = -spread / 2 + step * i;
    card.style.transform = `rotate(${angle}deg)`;
    card.classList.remove('card-selected');
  });
}

// 2) Función que maneja selección de cartas
function handleCardClick(e) {
  if (e.target.tagName !== 'IMG') return;

  const cards = deck.querySelectorAll('img');
  if (e.target.classList.contains('card-selected')) {
    e.target.classList.remove('card-selected');
  } else {
    cards.forEach(c => c.classList.remove('card-selected'));
    e.target.classList.add('card-selected');
  }
}

// 3) Inicialización al cargar el DOM
document.addEventListener('DOMContentLoaded', () => {
  // Mano del jugador
  window.deck = document.getElementById('deck');
  actualizarCartas(deck);
  deck.addEventListener('click', handleCardClick);

  // Mano del bot (dorsos)
  const deckOponente = document.getElementById('deck-oponente');
  const countOp = parseInt(deckOponente.dataset.count, 10) || 0;
  const rutaDorso = deckOponente.dataset.dorso;
  for (let i = 0; i < countOp; i++) {
    const img = document.createElement('img');
    img.src = rutaDorso;
    deckOponente.appendChild(img);
  }
  actualizarCartas(deckOponente);
});


  //3 Botón "Tomar Carta"
  document.getElementById('btn-tomar').addEventListener('click', () => {
    fetch('/tomar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        alert(data.error);
        return;
      }

      // Reconstruir mano del jugador
      deck.innerHTML = '';
      data.mano_jugador.forEach(carta => {
        const img = document.createElement('img');
        // Elegir src según tipo
        if (carta.tipo === 'CCOLOR') {
          img.src = '/static/img/CCOLOR.png';
        } else if (carta.tipo === 'NUM') {
          img.src = `/static/img/${carta.color}/NUM-${carta.valor}.png`;
        } else {
          img.src = `/static/img/${carta.color}/${carta.tipo}.png`;
        }
        // ===== Aquí asignamos los data-* para cada carta =====
        img.dataset.color = carta.color;
        img.dataset.tipo  = carta.tipo;
        img.dataset.valor = carta.valor !== null ? carta.valor : '';
        // =====================================================

        deck.appendChild(img);
      });

      // Volver a aplicar abanico y reactivar el click handler
      actualizarCartas(deck);
      deck.removeEventListener('click', handleCardClick);
      deck.addEventListener('click', handleCardClick);
    // 2) Actualizar carta tope
    const topeImg = document.getElementById('carta-tope');
    const ct = data.carta_tope;
    topeImg.src = ct.tipo === 'NUM'
      ? `/static/img/${ct.color}/NUM-${ct.valor}.png`
      : `/static/img/${ct.color}/${ct.tipo}.png`;
    topeImg.dataset.color = ct.color;
    topeImg.dataset.tipo = ct.tipo;
    topeImg.dataset.valor = ct.valor || '';
    // 3) Actualizar cartas del bot
    const deckBot = document.getElementById('deck-oponente');
    deckBot.innerHTML = '';
    for (let i = 0; i < data.cantidad_cartas_bot; i++) {
      const imgBack = document.createElement('img');
      imgBack.src = deckBot.dataset.dorso;
      deckBot.appendChild(imgBack);
    }
    actualizarCartas(deckBot);
    // 4) Acción del bot después de que el jugador tomó carta
    const ab = data.accion_bot;
    if (ab.accion === 'jugó' || ab.accion === 'robó_y_jugó') {
      const c = ab.carta;
      alert(`El bot jugó: ${c.tipo === 'NUM' ? c.color + ' ' + c.valor : c.color + ' ' + c.tipo}`);
    } else if (ab.accion === 'robó') {
      alert('El bot robó una carta.');
    }
  })
  .catch(err => {
    console.error(err);


    });
  });




//-------------------------------------------------

//4
//  Botón "Jugar Carta"
let colorElegido = null; 
document.getElementById('btn-jugar').addEventListener('click', () => {
  const seleccionada = deck.querySelector('.card-selected');
  if (!seleccionada) {
    alert('Debes seleccionar una carta primero.');
    return;
  }

  // 1) Preparar datos de la carta del jugador
const { color: colorSel, tipo: tipoSel, valor: valorSel } = seleccionada.dataset;
const payload = { color: colorSel, tipo: tipoSel, valor: valorSel };

if (tipoSel === "CCOLOR") {
  if (!colorElegido) {
    alert("Debes elegir un color antes de jugar la carta.");
    return;
  }
  payload.nuevo_color = colorElegido;
}
  // 2) Llamar al servidor
  console.log("Payload enviado:", payload);
  fetch('/jugar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      alert(data.error);
      return;
    }

    document.getElementById('selector-color').style.display = 'none';
    // 3) Reconstruir mano del jugador (por si robó cartas)
    deck.innerHTML = '';
    data.mano_jugador.forEach(carta => {
      const img = document.createElement('img');
      if (carta.tipo === 'CCOLOR') {
        img.src = `/static/img/${carta.color}/CCOLOR.png`;
      } else if (carta.tipo === 'NUM') {
        img.src = `/static/img/${carta.color}/NUM-${carta.valor}.png`;
      } else {
        img.src = `/static/img/${carta.color}/${carta.tipo}.png`;
      }
      img.dataset.color = carta.color;
      img.dataset.tipo  = carta.tipo;
      img.dataset.valor = carta.valor || '';
      deck.appendChild(img);
    });
    actualizarCartas(deck);
    deck.removeEventListener('click', handleCardClick);
    deck.addEventListener('click', handleCardClick);

    // 4) **Actualizar carta tope usando data.carta_tope** (después de bot incluido)
    const topeImg = document.getElementById('carta-tope');
    const ct = data.carta_tope;
    topeImg.src = ct.tipo === 'NUM'
      ? `/static/img/${ct.color}/NUM-${ct.valor}.png`
      : `/static/img/${ct.color}/${ct.tipo}.png`;
    topeImg.dataset.color = ct.color;
    topeImg.dataset.tipo  = ct.tipo;
    topeImg.dataset.valor = ct.valor || '';

    // 5) Actualizar dorsos del bot
    const deckBot = document.getElementById('deck-oponente');
    deckBot.innerHTML = '';
    for (let i = 0; i < data.cantidad_cartas_bot; i++) {
      const imgBack = document.createElement('img');
      imgBack.src = deckBot.dataset.dorso;
      deckBot.appendChild(imgBack);
    }
    actualizarCartas(deckBot);

    // 6) Mostrar alerta con lo que hizo el bot
    const ab = data.accion_bot;
    if (ab.accion === 'jugó' || ab.accion === 'robó_y_jugó') {
      const c = ab.carta;
      alert(`El bot jugó: ${c.tipo === 'NUM' ? c.color + ' ' + c.valor : c.color + ' ' + c.tipo}`);
    } else if (ab.accion === 'robó') {
      alert('El bot robó una carta.');
    }
  })
  .catch(err => {
    console.error(err);

  });
});




//-------------Btn "guardar Conexión DB"-------------------
document.getElementById('btn-guardar').addEventListener('click', () => {
  fetch('/guardar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})  // No necesitamos enviar datos; el servidor usa partida_actual
  })
  .then(res => res.json())
  .then(data => {
    if (data.ok) {
      alert('✅ Partida guardada correctamente.');
    } else {
      alert('❌ Error al guardar partida: ' + (data.error || 'Error desconocido'));
    }
  })
  .catch(err => {
    console.error(err);
    alert('❌ No se pudo conectar al servidor para guardar.');
  });
});
//CColor
// Mostrar el selector de color si se elige una carta CCOLOR
deck.addEventListener('click', () => {
  const seleccionada = deck.querySelector('.card-selected');
  if (!seleccionada) return;

  const tipo = seleccionada.dataset.tipo;
  const colorSelector = document.getElementById('selector-color');

  if (tipo === "CCOLOR") {
    colorSelector.style.display = 'block';
  } else {
    colorSelector.style.display = 'none';
    colorElegido = null;
  }
});

// Manejar clic en los botones de color
document.querySelectorAll('.color-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    colorElegido = btn.dataset.color;
    alert(`Color elegido: ${colorElegido}`);
  });
});
