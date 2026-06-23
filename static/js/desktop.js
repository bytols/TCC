/* ══════════════════════════════════════════════════
   RUÍDO — Desktop (TV) controller
   Single socket + polling fallback. Real-time players + progress.
══════════════════════════════════════════════════ */
(function () {
  const app = document.getElementById("desktop-app");
  const STATE = app ? app.dataset.state : null;
  const socket = io();

  socket.on("connect", function () { socket.emit("desktop_connect"); });
  socket.on("state_change", function (d) { if (d.state !== STATE) window.location.reload(); });
  socket.on("session_ended", function () { window.location.reload(); });
  socket.on("player_joined", function (d) { renderPlayers(d.players, d.player_count); });
  socket.on("player_left", function (d) { syncPlayers(d.players, d.player_count); });
  socket.on("progress", function (d) { renderProgress(d.submitted, d.total, d.submitted_ids); });

  /* ── Cor de fundo a partir do evento round_phase do servidor ── */
  const GLOWS = ["glow-blue", "glow-pink", "glow-orange", "glow-final", "glow-green"];
  const COLOR_MAP = { BLUE: "glow-blue", PINK: "glow-pink", ORANGE: "glow-orange", GREEN: "glow-green" };
  function applyGlow(cls) {
    if (!app || app.classList.contains(cls)) return;
    GLOWS.forEach(function (c) { app.classList.remove(c); });
    app.classList.add(cls);
  }
  // Cor inicial a partir do estado renderizado (sem depender de elapsed_seconds)
  (function () {
    if (STATE === "FINAL") applyGlow("glow-green");
    else if (STATE === "LOBBY") applyGlow("glow-final");
    else if (STATE && STATE.startsWith("ROUND_")) applyGlow("glow-blue");
    else if (STATE === "SHOW_1") applyGlow("glow-blue");
    else if (STATE === "SHOW_2") applyGlow("glow-pink");
  }());
  // Atualiza cor em tempo real a partir do servidor
  socket.on("round_phase", function (d) { applyGlow(COLOR_MAP[d.color] || "glow-blue"); });

  /* ── Render lobby grid + waiting avatars ── */
  function renderPlayers(players, count) {
    const countEl = document.getElementById("participant-count");
    if (countEl) countEl.textContent = count + "/10";

    const grid = document.getElementById("players-grid");
    if (grid) {
      const empty = grid.querySelector(".players-empty");
      if (empty && players.length) empty.remove();
      players.forEach(function (pl) {
        if (!document.getElementById("player-" + pl.id)) {
          const div = document.createElement("div");
          div.className = "player-card";
          div.id = "player-" + pl.id;
          div.innerHTML = (pl.avatar_path
            ? '<img src="' + pl.avatar_path + '" class="player-avatar" alt="">'
            : '<div class="player-avatar-placeholder">' + pl.name.charAt(0).toUpperCase() + "</div>")
            + '<span class="player-name">' + pl.name + "</span>";
          grid.appendChild(div);
        }
      });
    }

    // waiting (round) avatar chips
    const wrap = document.getElementById("waiting-players");
    if (wrap) {
      players.forEach(function (pl) {
        if (!document.getElementById("wp-" + pl.id)) {
          const chip = document.createElement("div");
          chip.className = "waiting-player-chip";
          chip.id = "wp-" + pl.id;
          chip.innerHTML = (pl.avatar_path ? '<img src="' + pl.avatar_path + '" class="chip-avatar" alt="">' : "")
            + "<span>" + pl.name + "</span>";
          wrap.appendChild(chip);
        }
      });
    }

    // botão Iniciar reativo (onclick já está no HTML; aqui só alterna estado)
    const startBtn = document.getElementById("start-btn");
    if (startBtn) {
      startBtn.disabled = count < 2;
      startBtn.textContent = count >= 2 ? "INICIAR" : "AGUARDANDO JOGADORES...";
    }

    // Countdown auto-start: inicia quando há ≥2 jogadores, cancela se cair abaixo de 2
    if (STATE === "LOBBY") {
      if (count >= 2) {
        startCountdown();
      } else {
        cancelCountdown();
      }
    }
  }

  /* ── Countdown auto-start (30s por padrão, configurável via AUTO_START_SECONDS) ── */
  var _countdownTimer = null;
  var _countdownRunning = false;

  function startCountdown() {
    if (_countdownRunning) return; // não reinicia se já está rodando
    _countdownRunning = true;
    var seconds = (typeof window.AUTO_START_SECONDS === "number") ? window.AUTO_START_SECONDS : 30;
    var display = document.getElementById("countdown-display");
    if (display) {
      display.style.display = "";
      display.textContent = "Começando em " + seconds + "s";
    }
    _countdownTimer = setInterval(function () {
      seconds -= 1;
      if (display) display.textContent = "Começando em " + seconds + "s";
      if (seconds <= 0) {
        cancelCountdown();
        fetch("/admin/start", { method: "POST" })
          .then(function (r) { return r.json(); })
          .then(function () { window.location.reload(); })
          .catch(function () {});
      }
    }, 1000);
  }

  function cancelCountdown() {
    if (_countdownTimer !== null) {
      clearInterval(_countdownTimer);
      _countdownTimer = null;
    }
    _countdownRunning = false;
    var display = document.getElementById("countdown-display");
    if (display) display.style.display = "none";
  }

  /* ── Sincroniza o elenco: adiciona novos e REMOVE quem saiu/caiu ── */
  function syncPlayers(players, count) {
    renderPlayers(players, count);
    const ids = players.map(function (p) { return String(p.id); });
    [["players-grid", "player-"], ["waiting-players", "wp-"]].forEach(function (pair) {
      const grid = document.getElementById(pair[0]);
      if (!grid) return;
      const prefix = pair[1];
      Array.prototype.slice.call(grid.children).forEach(function (child) {
        if (child.id && child.id.indexOf(prefix) === 0
            && ids.indexOf(child.id.slice(prefix.length)) === -1) {
          child.remove();
        }
      });
    });
  }

  /* ── Render collective progress (item: "X de Y concluíram") ── */
  function renderProgress(submitted, total, ids) {
    const el = document.getElementById("waiting-progress");
    if (el) el.textContent = submitted + " de " + total + " participantes concluíram";
    if (ids) {
      ids.forEach(function (id) {
        const chip = document.getElementById("wp-" + id);
        if (chip) chip.classList.add("done");
      });
    }
  }

  /* ── Polling fallback (works even if WS drops) ── */
  setInterval(function () {
    fetch("/api/lobby_state")
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.state !== STATE) { window.location.reload(); return; }
        if (d.players) syncPlayers(d.players, d.player_count);
        if (d.progress) renderProgress(d.progress.submitted, d.progress.total, d.progress.submitted_ids);
      })
      .catch(function () {});
  }, 2500);
}());

/* ── Admin controls (global, called from onclick) ── */
function startSession() {
  fetch("/admin/start", { method: "POST" }).then(function (r) { return r.json(); })
    .then(function () { window.location.reload(); });
}
function advanceSession() {
  fetch("/admin/advance", { method: "POST" }).then(function (r) { return r.json(); })
    .then(function () { window.location.reload(); });
}
function endSession() {
  if (confirm("Encerrar a partida? Todos os jogadores serão desconectados e a tela volta ao início.")) {
    fetch("/admin/end", { method: "POST" }).then(function () { window.location.reload(); });
  }
}
