self.onmessage = function(e) {
  let numero = 1.000000000054;
  for(let i = 0;i<10000000000;i++){
    numero *= 1.000000000043;
  }
  postMessage("finalizado");
};
