/* ══════════════════════════════════════════════════
   RUÍDO — Seleção (rounds 1/2/3)
   Grid de gêneros (round 1) → deck cíclico estilo Tinder → modal view-only
══════════════════════════════════════════════════ */
const MOVIES_DATA = JSON.parse(document.getElementById('movies-data').textContent);
const selectedGenres = new Set();
const selected = new Set();        // ids dos filmes escolhidos
const movieById = {};
let items = [];                    // filmes do deck atual
let pos = 0;                       // índice central (cíclico)
let cards = [];                    // elementos .deck-card

Object.entries(MOVIES_DATA).forEach(([catKey, cat]) => {
  (cat.movies || []).forEach(m => {
    movieById[m.id] = { ...m, cat: catKey, catLabel: cat.label, color: cat.color };
  });
});

/* ── rating + sinopse determinísticos (não existem nos dados) ── */
function hashStr(s) { let h = 0; for (let i = 0; i < s.length; i++) { h = (h * 31 + s.charCodeAt(i)) | 0; } return Math.abs(h); }
function ratingFor(id) { return (3.7 + (hashStr(id) % 14) / 10).toFixed(1); }
const SYNOPSIS = {
  acao:     ['Adrenalina pura: perseguições, confrontos e um herói no limite.', 'Explosões, reviravoltas e uma corrida contra o tempo.'],
  animacao: ['Uma jornada colorida que encanta todas as idades.', 'Aventura animada cheia de coração e imaginação.'],
  comedia:  ['Risadas garantidas em uma trama leve e cheia de situações inusitadas.', 'Humor afiado e personagens que conquistam de cara.'],
  documentario: ['Uma imersão real em histórias que parecem ficção.', 'O mundo como ele é, sem roteiro.'],
  drama:    ['Uma história intensa sobre escolhas, perdas e recomeços.', 'Emoção e profundidade humana em cada cena.'],
  fantasia: ['Mundos mágicos onde o impossível ganha vida.', 'Criaturas, reinos e destinos extraordinários.'],
  ficcao:   ['Mundos futuristas e questões que desafiam a realidade.', 'Tecnologia, mistério e o desconhecido além das estrelas.'],
  herois:   ['Poderes, responsabilidade e batalhas épicas.', 'Quando pessoas comuns se tornam lendas.'],
  romance:  ['Um encontro que muda tudo — paixão, dúvidas e destino.', 'Amor em sua forma mais sincera e arrebatadora.'],
  sitcom:   ['Confusões cotidianas e um elenco que vira família.', 'Humor leve para rir do começo ao fim.'],
  suspense: ['Tensão crescente até uma reviravolta que ninguém espera.', 'Cada pista esconde um segredo perigoso.'],
  terror:   ['O medo espreita em cada canto desta experiência arrepiante.', 'Sustos, atmosfera densa e o terror que não dá trégua.'],
};
function synopsisFor(m) {
  const pool = SYNOPSIS[m.cat] || ['Uma escolha marcante para a noite do grupo.'];
  return pool[hashStr(m.id) % pool.length];
}
function posterGradient(color) { return `linear-gradient(155deg, ${color}66 0%, rgba(6,5,26,0.96) 100%)`; }

/* ════════════ Round 1: grid de gêneros (item 3) ════════════ */
function toggleGenre(catKey, el) {
  if (selectedGenres.has(catKey)) { selectedGenres.delete(catKey); el.classList.remove('selected'); }
  else { selectedGenres.add(catKey); el.classList.add('selected'); }
  document.getElementById('btn-see-movies').disabled = selectedGenres.size === 0;
}

function showMoviePhase() {
  const cats = Object.keys(MOVIES_DATA).filter(c => selectedGenres.has(c));
  buildDeck(cats);
  document.getElementById('phase-cat').style.display = 'none';
  document.getElementById('phase-movies').style.display = 'flex';
  document.getElementById('selected-counter').style.display = '';
  document.getElementById('round-instruction-text').textContent = MOVIE_INSTRUCTION;
}

/* ════════════ Deck cíclico estilo Tinder (itens 4/5) ════════════ */
function buildDeck(catKeys) {
  items = [];
  (catKeys && catKeys.length ? catKeys : Object.keys(MOVIES_DATA)).forEach(c => {
    (MOVIES_DATA[c].movies || []).forEach(m => items.push(movieById[m.id]));
  });

  const deck = document.getElementById('deck');
  deck.innerHTML = '';
  cards = items.map((m, i) => {
    const card = document.createElement('div');
    card.className = 'deck-card';
    card.dataset.i = i;
    card.dataset.id = m.id;
    card.innerHTML =
      '<div class="deck-poster" style="background:' + posterGradient(m.color) + '">' +
        '<span class="deck-initial">' + m.title.charAt(0) + '</span>' +
        '<div class="deck-check">✓</div>' +
      '</div>';
    deck.appendChild(card);
    return card;
  });

  pos = 0;
  attachGestures(deck);
  layout();
}

function cyclicRel(i) {
  const n = items.length;
  let r = i - pos;
  if (r > n / 2) r -= n;
  if (r < -n / 2) r += n;
  return r;
}

function layout() {
  cards.forEach((card, i) => {
    const r = cyclicRel(i);
    let tx, sc, rot, op, z, pe;
    if (r === 0)       { tx = '0';     sc = 1;   rot = '0deg';   op = 1;   z = 30; pe = 'auto'; }
    else if (r === -1) { tx = '-64%';  sc = .8;  rot = '-9deg';  op = .5;  z = 20; pe = 'auto'; }
    else if (r === 1)  { tx = '64%';   sc = .8;  rot = '9deg';   op = .5;  z = 20; pe = 'auto'; }
    else if (r === -2) { tx = '-108%'; sc = .66; rot = '-13deg'; op = .15; z = 10; pe = 'none'; }
    else if (r === 2)  { tx = '108%';  sc = .66; rot = '13deg';  op = .15; z = 10; pe = 'none'; }
    else               { tx = (r < 0 ? '-135%' : '135%'); sc = .6; rot = '0deg'; op = 0; z = 1; pe = 'none'; }
    card.style.setProperty('--tx', tx);
    card.style.setProperty('--sc', sc);
    card.style.setProperty('--rot', rot);
    card.style.setProperty('--op', op);
    card.style.zIndex = z;
    card.style.pointerEvents = pe;
    card.classList.toggle('focused', r === 0);
    card.classList.toggle('in-list', selected.has(items[i].id));
  });
  renderMeta();
}

function go(dir) {
  const n = items.length;
  if (n <= 1) return;
  pos = (pos + dir + n) % n;
  layout();
}

/* swipe (arraste) + tap, sem disparo duplo */
function attachGestures(deck) {
  let startX = null;
  deck.onpointerdown = (e) => { startX = e.clientX; };
  deck.onpointerup = (e) => {
    if (startX === null) return;
    const dx = e.clientX - startX; startX = null;
    if (Math.abs(dx) > 40) { go(dx < 0 ? 1 : -1); return; }   // swipe
    const card = e.target.closest('.deck-card');              // tap
    if (!card) return;
    const r = cyclicRel(+card.dataset.i);
    if (r === 0) openModal(card.dataset.id);
    else go(r > 0 ? 1 : -1);
  };
  deck.onpointercancel = () => { startX = null; };
}

function renderMeta() {
  const m = items[pos];
  if (!m) return;
  document.getElementById('meta-title').textContent = m.title;
  document.getElementById('meta-sub').textContent =
    (m.year ? m.year + ' · ' : '') + m.catLabel + ' · ★ ' + ratingFor(m.id);
  syncAddBtn();
}

/* ════════════ Seleção (ação externa ao modal) ════════════ */
function syncAddBtn() {
  const btn = document.getElementById('btn-add');
  const m = items[pos];
  if (!m) return;
  const inList = selected.has(m.id);
  btn.classList.toggle('added', inList);
  btn.textContent = inList ? '✓ ADICIONADO' : '+ ADICIONAR À MINHA LISTA';
  btn.disabled = selected.size >= PICKS_REQUIRED && !inList;
}

function toggleCurrent() {
  const m = items[pos];
  if (!m) return;
  if (selected.has(m.id)) selected.delete(m.id);
  else { if (selected.size >= PICKS_REQUIRED) return; selected.add(m.id); }
  cards[pos].classList.toggle('in-list', selected.has(m.id));
  updateCounter();
  syncAddBtn();
}

function updateCounter() {
  const count = selected.size;
  const cEl = document.getElementById('selected-count');
  if (cEl) cEl.textContent = count;
  const counter = document.getElementById('selected-counter');
  if (counter) counter.classList.toggle('is-complete', count === PICKS_REQUIRED);
  const btn = document.getElementById('submit-btn');
  btn.disabled = count !== PICKS_REQUIRED;
  btn.textContent = btn.dataset.label + ' (' + count + '/' + PICKS_REQUIRED + ')';
}

function submitChoices() {
  if (selected.size !== PICKS_REQUIRED) return;
  const holder = document.getElementById('hidden-inputs');
  holder.innerHTML = '';
  selected.forEach(id => {
    const input = document.createElement('input');
    input.type = 'hidden'; input.name = 'movie_ids'; input.value = id;
    holder.appendChild(input);
  });
  document.getElementById('round-form').submit();
}

/* ════════════ Modal — apenas visualização (item 4) ════════════ */
function openModal(id) {
  const m = movieById[id];
  if (!m) return;
  document.getElementById('modal-bg').style.background = posterGradient(m.color);
  const poster = document.getElementById('modal-poster');
  poster.style.background = posterGradient(m.color);
  poster.textContent = m.title.charAt(0);
  document.getElementById('modal-title').textContent = m.title;
  document.getElementById('modal-year').textContent = m.year || '—';
  document.getElementById('modal-genre').textContent = m.catLabel;
  document.getElementById('modal-rating').textContent = '★ ' + ratingFor(m.id);
  document.getElementById('modal-synopsis').textContent = synopsisFor(m);
  document.getElementById('movie-modal').classList.add('open');
}
function closeModal() { document.getElementById('movie-modal').classList.remove('open'); }
document.getElementById('movie-modal').addEventListener('click', (e) => {
  if (e.target.id === 'movie-modal' || e.target.classList.contains('movie-modal-overlay')) closeModal();
});

/* ════════════ Init ════════════ */
(function init() {
  const btn = document.getElementById('submit-btn');
  btn.dataset.label = btn.textContent.replace(/\s*\(.*\)\s*$/, '').trim();
  updateCounter();
  if (!SHOW_GENRES) {
    buildDeck(Object.keys(MOVIES_DATA));   // rounds 2/3: deck direto sobre o pool
  }
})();
