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
  socket.on("progress", function (d) { renderProgress(d.submitted, d.total, d.submitted_ids); });

  /* ── Cor de fundo dinâmica por tempo decorrido (item 10) ── */
  const GLOWS = ["glow-blue", "glow-pink", "glow-orange", "glow-final", "glow-green"];
  function colorClassFor(elapsed, state) {
    if (state === "FINAL") return "glow-green";   // consenso → verde
    if (state === "LOBBY") return "glow-final";   // lobby quente
    if (elapsed < 180) return "glow-blue";        // 0–3 min · exploração
    if (elapsed < 360) return "glow-pink";        // 3–6 min · aproximação
    return "glow-orange";                          // 6+ min · negociação
  }
  function applyColor(elapsed, state) {
    if (!app) return;
    const cls = colorClassFor(elapsed, state);
    if (app.classList.contains(cls)) return;
    GLOWS.forEach(function (c) { app.classList.remove(c); });
    app.classList.add(cls);   // transição suave via CSS (background-color 2s)
  }
  // aplica imediatamente com o tempo embutido no HTML (evita flash)
  applyColor(parseInt(app && app.dataset.elapsed || "0", 10), STATE);
  // avança a cor mesmo sem novos eventos (ex.: 3min → rosa) a cada 5s
  let localElapsed = parseInt(app && app.dataset.elapsed || "0", 10);
  setInterval(function () { localElapsed += 5; applyColor(localElapsed, STATE); }, 5000);

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

    // enable start button at >= 2
    const startBtn = document.querySelector(".btn-start");
    if (startBtn && count >= 2) {
      startBtn.disabled = false;
      startBtn.classList.remove("btn-disabled");
      startBtn.textContent = "INICIAR";
    }
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
        if (d.players) renderPlayers(d.players, d.player_count);
        if (d.progress) renderProgress(d.progress.submitted, d.progress.total, d.progress.submitted_ids);
        if (typeof d.elapsed_seconds === "number") {
          localElapsed = d.elapsed_seconds;     // sincroniza com o servidor
          applyColor(localElapsed, d.state);
        }
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
  if (confirm("Encerrar a sessão e limpar todos os dados?")) {
    fetch("/admin/end", { method: "POST" }).then(function () { window.location.reload(); });
  }
}
