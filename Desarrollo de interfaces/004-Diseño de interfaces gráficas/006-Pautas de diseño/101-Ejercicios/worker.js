// worker.js
// Lógica de física (interacciones y movimiento) en un Web Worker

function distancia2D(x1, y1, x2, y2) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  return Math.sqrt(dx * dx + dy * dy);
}

let particulas = [];
let clavesPropiedades = [];
let usarEnRelacion = {};
let ancho = 0;
let alto  = 0;

onmessage = function(e){
  const datos = e.data;

  if (datos.tipo === "inicializar"){
    particulas = datos.particulas || [];
    clavesPropiedades = datos.clavesPropiedades || [];
    usarEnRelacion = datos.usarEnRelacion || {};
    ancho = datos.ancho || 0;
    alto  = datos.alto  || 0;

    postMessage({ tipo: "iniciado" });
  }
  else if (datos.tipo === "paso"){
    usarEnRelacion    = datos.usarEnRelacion || usarEnRelacion;
    clavesPropiedades = datos.clavesPropiedades || clavesPropiedades;

    calcularPasoFisica();
    postMessage({ tipo: "estado", particulas: particulas });
  }
  else if (datos.tipo === "reactivar"){
    // Quitar estado de "fija" para todas las partículas
    if (particulas) {
      for (let i = 0; i < particulas.length; i++){
        particulas[i].fija = false;
        particulas[i].estableFrames = 0;
      }
    }
  }
};

function calcularPasoFisica(){
  if (!particulas || particulas.length === 0) return;

  const n = particulas.length;

  const rangoGlobal = Math.sqrt(ancho*ancho + alto*alto);

  const distanciaObjetivo          = 120;
  const distanciaMinima            = 70;
  const distanciaRepulsionDistinto = 220;

  const kAtraccionFuerte   = 0.0015;
  const kAtraccionMedia    = 0.0009;
  const kRepulsionDistinto = 0.001;
  const kRepulsionCorta    = 0.06;

  const friccion = 0.93;
  const maxFuerza = 0.05;

  // Reiniciar aceleraciones
  for (let i = 0; i < n; i++){
    particulas[i].ax = 0;
    particulas[i].ay = 0;
  }

  // Calcular fuerzas de interacción
  for (let i = 0; i < n; i++){
    const p = particulas[i];
    if (p.fija) continue;

    let fx = 0;
    let fy = 0;

    for (let j = 0; j < n; j++){
      if (i === j) continue;
      const q = particulas[j];

      let d = distancia2D(p.x, p.y, q.x, q.y);
      if (d === 0 || d > rangoGlobal) continue;

      let dx = q.x - p.x;
      let dy = q.y - p.y;

      let ux = dx / d;
      let uy = dy / d;

      // Repulsión fuerte para evitar solapamiento
      if (d < distanciaMinima){
        let intensidad = (distanciaMinima - d) * kRepulsionCorta;
        fx -= ux * intensidad;
        fy -= uy * intensidad;
        continue;
      }

      // Coincidencias según propiedades activas en relación
      const propsCoinciden = [];
      let hayPropsRelacionActivas = false;
      for (const prop of clavesPropiedades){
        if (!usarEnRelacion[prop]) continue;
        hayPropsRelacionActivas = true;
        if (p.datos[prop] === q.datos[prop]){
          propsCoinciden.push(prop);
        }
      }

      if (propsCoinciden.length > 1){
        // Atracción fuerte (coinciden varias propiedades)
        let delta = d - distanciaObjetivo;
        fx += ux * delta * kAtraccionFuerte;
        fy += uy * delta * kAtraccionFuerte;

      } else if (propsCoinciden.length === 1){
        // Atracción media (coincide una propiedad)
        let delta = d - distanciaObjetivo;
        fx += ux * delta * kAtraccionMedia;
        fy += uy * delta * kAtraccionMedia;

      } else {
        // Sin coincidencias: repulsión suave si está relativamente cerca
        if (d < distanciaRepulsionDistinto){
          let intensidad = (distanciaRepulsionDistinto - d) * kRepulsionDistinto;
          fx -= ux * intensidad;
          fy -= uy * intensidad;
        }
      }
    }

    // Limitar fuerza total
    let modulo = Math.sqrt(fx*fx + fy*fy);
    if (modulo > maxFuerza){
      fx = fx / modulo * maxFuerza;
      fy = fy / modulo * maxFuerza;
    }

    p.ax = fx;
    p.ay = fy;
  }

  // Integrar movimiento y rebotes
  for (let i = 0; i < n; i++){
    const p = particulas[i];
    if (!p.fija){
      // Integrar aceleración -> velocidad
      p.vx += p.ax;
      p.vy += p.ay;

      // Fricción
      p.vx *= friccion;
      p.vy *= friccion;

      // Integrar velocidad -> posición
      p.x += p.vx;
      p.y += p.vy;

      // Rebote con bordes
      const reboteFactor = -0.5;

      if (p.x > ancho){
        p.x = ancho;
        p.vx *= reboteFactor;
      }
      if (p.x < 0){
        p.x = 0;
        p.vx *= reboteFactor;
      }
      if (p.y > alto){
        p.y = alto;
        p.vy *= reboteFactor;
      }
      if (p.y < 0){
        p.y = 0;
        p.vy *= reboteFactor;
      }

      // Comprobar estabilidad para fijar partícula
      const velocidad = Math.sqrt(p.vx*p.vx + p.vy*p.vy);
      const fuerza    = Math.sqrt(p.ax*p.ax + p.ay*p.ay);
      if (velocidad < 0.02 && fuerza < 0.002){
        p.estableFrames = (p.estableFrames || 0) + 1;
        if (p.estableFrames > 60){
          p.fija = true;
          p.vx = 0;
          p.vy = 0;
        }
      } else {
        p.estableFrames = 0;
      }
    }
  }
}

