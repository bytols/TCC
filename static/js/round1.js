const selectedMovies = new Set();
const selectedCats = new Set();

function toggleCategory(catKey, el) {
  if (selectedCats.has(catKey)) {
    selectedCats.delete(catKey);
    el.classList.remove('selected');
  } else {
    selectedCats.add(catKey);
    el.classList.add('selected');
  }
  document.getElementById('btn-see-movies').disabled = selectedCats.size === 0;
}

function showMoviePhase() {
  document.querySelectorAll('.movie-card').forEach(function(card) {
    card.style.display = selectedCats.has(card.dataset.cat) ? '' : 'none';
  });

  const bar = document.getElementById('active-cats-bar');
  bar.innerHTML = '';
  selectedCats.forEach(function(catKey) {
    const tile = document.querySelector('.cat-tile[data-cat="' + catKey + '"]');
    if (tile) {
      const chip = document.createElement('span');
      chip.className = 'active-cat-chip';
      chip.textContent = tile.querySelector('.cat-tile-name').textContent;
      chip.style.setProperty('--cat-color', getComputedStyle(tile).getPropertyValue('--cat-color').trim());
      bar.appendChild(chip);
    }
  });

  document.getElementById('phase-cat').style.display = 'none';
  document.getElementById('phase-movies').style.display = '';
  document.getElementById('round-footer').style.display = '';
  document.getElementById('selected-counter').style.display = '';
  document.getElementById('round-instruction-text').textContent =
    'ESCOLHA ' + PICKS_REQUIRED + ' FILMES';
}

function showCatPhase() {
  document.getElementById('phase-movies').style.display = 'none';
  document.getElementById('round-footer').style.display = 'none';
  document.getElementById('selected-counter').style.display = 'none';
  document.getElementById('phase-cat').style.display = '';
  document.getElementById('round-instruction-text').textContent =
    'ESCOLHA AS CATEGORIAS QUE MAIS TE AGRADAM';
}

function updateCounter() {
  const count = selectedMovies.size;
  const countEl = document.getElementById('selected-count');
  const btn = document.getElementById('submit-btn');
  if (countEl) countEl.textContent = count;
  if (btn) {
    btn.disabled = count !== PICKS_REQUIRED;
    btn.textContent = 'CONFIRMAR ESCOLHAS (' + count + '/' + PICKS_REQUIRED + ')';
  }
}

document.querySelectorAll('.movie-checkbox').forEach(function(cb) {
  cb.addEventListener('change', function() {
    const movieId = cb.value;
    const card = cb.closest('.movie-card');
    if (cb.checked) {
      if (selectedMovies.size >= PICKS_REQUIRED) {
        cb.checked = false;
        return;
      }
      selectedMovies.add(movieId);
      card.classList.add('selected');
    } else {
      selectedMovies.delete(movieId);
      card.classList.remove('selected');
    }
    updateCounter();
  });
});

updateCounter();
