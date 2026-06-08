// Desktop Socket.io client — keeps the view in sync without full page reloads.
// State changes that differ from current reload the page so the server renders the new panel.
(function () {
  const socket = io();

  socket.on("connect", function () {
    socket.emit("desktop_connect");
  });

  socket.on("session_ended", function () {
    window.location.reload();
  });
}());
