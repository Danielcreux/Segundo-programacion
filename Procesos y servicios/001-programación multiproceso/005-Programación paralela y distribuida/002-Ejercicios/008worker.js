self.onmessage = function(e) {
  let datos = e.data;
  for(let i = 0;i<datos.length;i++){
    datos[i] = datos[i].toUpperCase();
  }
  postMessage(datos);
};
