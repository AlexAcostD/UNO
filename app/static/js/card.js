
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

  
  document.addEventListener('DOMContentLoaded', () => {
    const deck = document.getElementById('deck');
    actualizarCartas(deck);
    deck.addEventListener('click', handleCardClick);
    
    const deckOponente=document.getElementById('deck-oponente')
    const count=parseInt(deckOponente.dataset.count, 10) || 0
    const rutaDorso = deckOponente.dataset.dorso


    for (let i = 0; i < count; i++) {
    const img = document.createElement('img');
    img.src = rutaDorso;
    deckOponente.appendChild(img);
    }

    actualizarCartas(deckOponente);
    
  });