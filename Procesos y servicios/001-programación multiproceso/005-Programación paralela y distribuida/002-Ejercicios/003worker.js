self.onmessage = function(e) {
  postMessage("Hola desde el worker de vuelta al hilo principal");
};
