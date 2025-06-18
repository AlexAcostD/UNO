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

  // Botón "Tomar Carta"
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
    });
  });

  // Botón "Jugar Carta"
  document.getElementById('btn-jugar').addEventListener('click', () => {
    const seleccionada = deck.querySelector('.card-selected');
    if (!seleccionada) {
      alert('Debes seleccionar una carta primero.');
      return;
    }
    const topeImg = document.getElementById('carta-tope');
    const { color: colorSel, tipo: tipoSel, valor: valorSel } = seleccionada.dataset;
    const { color: colorTope, tipo: tipoTope, valor: valorTope } = topeImg.dataset;

    let esCompatible = false;
    if (tipoSel === 'CCOLOR') {
      esCompatible = true;
    } else if (colorSel === colorTope) {
      esCompatible = true;
    } else if (tipoSel === 'NUM' && tipoTope === 'NUM' && valorSel === valorTope) {
      esCompatible = true;
    }

    if (!esCompatible) {
      alert('Esa carta no se puede jugar. Debe coincidir en color o número.');
      return;
    }

    // Reemplaza la carta tope visualmente
    topeImg.src = seleccionada.src;
    topeImg.dataset.color = colorSel;
    topeImg.dataset.tipo  = tipoSel;
    topeImg.dataset.valor = valorSel;

    // Quita la carta jugada del deck
    seleccionada.remove();

    // Reaplica abanico
    actualizarCartas(deck);

    alert(`¡Carta jugada: ${tipoSel === 'NUM' ? colorSel + ' ' + valorSel : colorSel + ' ' + tipoSel}!`);
  });
});
