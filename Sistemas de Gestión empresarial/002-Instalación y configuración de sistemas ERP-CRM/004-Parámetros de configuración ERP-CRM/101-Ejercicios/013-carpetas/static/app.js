// ======= DOM refs =======
const centro = document.getElementById("centro");
const mundo  = document.getElementById("mundo");
const edgesSvg = document.getElementById("edges");
const toolsList = document.getElementById("tools-list");
const playBtn = document.getElementById("play");
const logEl = document.getElementById("log");

// ======= State =======
const nodos  = [];      // {id, x, y, el, type, config}
const conexiones = [];  // {from, to, pathBg, path, glow}
let nodoCounter = 1;
let TOOLS = [];

let scale = 1, translateX = 0, translateY = 0;
function aplicarTransform(){ mundo.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`; }
function clamp(v,a,b){ return Math.max(a, Math.min(b, v)); }
function screenToWorld(x, y){
  const rect = centro.getBoundingClientRect();
  return { x: (x - rect.left - translateX) / scale, y: (y - rect.top  - translateY) / scale };
}
aplicarTransform();

function log(msg){
  const at = new Date().toLocaleTimeString();
  logEl.textContent = `[${at}] ${msg}\n` + logEl.textContent;
}

// ======= Load tools =======
fetch("/api/tools").then(r=>r.json()).then(d=>{
  TOOLS = d.tools || [];
  if(!TOOLS.length){ toolsList.innerHTML = '<div class="muted">No hay tools</div>'; return; }
  toolsList.innerHTML = "";
  TOOLS.forEach(t=>{
    const card = document.createElement("div");
    card.className = "tool-card";
    card.innerHTML = `<div><strong>${t.label}</strong></div><div class="tool-desc">${t.description}</div>`;
    const btn = document.createElement("button");
    btn.className = "btn-add";
    btn.textContent = "Añadir como nodo";
    btn.addEventListener("click", ()=> crearNodoTool(t));
    card.appendChild(btn);
    toolsList.appendChild(card);
  });
});

// ======= Node creation =======
function crearNodoBase(x, y, title){
  const el = document.createElement("article");
  el.style.left = x + "px";
  el.style.top  = y + "px";
  el.innerHTML = `
    <div class="titlebar drag-handle"></div>
    <div class="title">${title}</div>
    <div class="body"></div>
    <div class="port in"  title="Entrada"></div>
    <div class="port out" title="Salida"></div>
  `;
  mundo.appendChild(el);
  return el;
}

function crearNodoTool(tool){
  const rect = centro.getBoundingClientRect();
  const screenX = rect.width/2, screenY = rect.height/2;
  const worldX = (screenX - translateX) / scale - parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nodo-w'))/2;
  const worldY = (screenY - translateY) / scale - parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nodo-h'))/2;

  const el = crearNodoBase(Math.round(worldX), Math.round(worldY), tool.label);
  const body = el.querySelector(".body");

  // Build config UI
  body.innerHTML = "";
  Object.entries(tool.config || {}).forEach(([key, cfg])=>{
    const row = document.createElement("div");
    row.className = "form-row";
    const id = `cfg_${nodoCounter}_${key}`;
    row.innerHTML = `
      <label for="${id}">${cfg.label || key}</label>
      <input id="${id}" type="text" value="${cfg.default ?? ''}" placeholder="${cfg.placeholder ?? ''}">
    `;
    body.appendChild(row);
  });

  const nodo = {
    id: `n${nodoCounter++}`,
    x: worldX, y: worldY,
    el, type: tool.type,
    config: {}
  };
  el.dataset.index = (nodos.length).toString();
  nodos.push(nodo);

  const portIn  = el.querySelector('.port.in');
  const portOut = el.querySelector('.port.out');
  const handle  = el.querySelector('.drag-handle'); // <<< SOLO esta zona arrastra el nodo

  // --- Drag del nodo SOLO desde la barra de título ---
  handle.addEventListener("mousedown", (e)=>{
    if(e.ctrlKey) return; // pan global
    iniciarDragNodo(e, el);
  });

  // Importante: permitir que inputs sean interactivos
  // (No ponemos listeners de drag en 'el' completo para no interferir con inputs)

  // Start connection from OUT
  portOut.addEventListener("mousedown", (e)=>{ e.stopPropagation(); iniciarConexionDesdeSalida(e, el, portOut); });
  // Finish at IN
  portIn.addEventListener("mouseup", (e)=>{ e.stopPropagation(); if(conexionEnCurso) finalizarConexionEnEntrada(el, portIn); });

  return nodo;
}

// ======= Drag nodes =======
let dragging = null, startMouseX=0, startMouseY=0, startLeft=0, startTop=0;

function iniciarDragNodo(e, el){
  e.preventDefault();
  dragging = el;
  el.classList.add("dragging");
  startMouseX = e.clientX; startMouseY = e.clientY;
  startLeft = parseFloat(el.style.left)||0; startTop = parseFloat(el.style.top)||0;
  document.addEventListener("mousemove", moverDragNodo);
  document.addEventListener("mouseup", terminarDragNodo);
}
function moverDragNodo(e){
  if(!dragging) return;
  const nx = startLeft + (e.clientX - startMouseX) / scale;
  const ny = startTop  + (e.clientY - startMouseY) / scale;
  posicionarEnMundo(dragging, nx, ny);
  const idx = parseInt(dragging.dataset.index,10);
  actualizarConexionesDeNodo(idx);
}
function terminarDragNodo(){
  if(!dragging) return;
  const idx = parseInt(dragging.dataset.index,10);
  const nodo = nodos[idx];
  nodo.x = parseFloat(dragging.style.left)||0;
  nodo.y = parseFloat(dragging.style.top)||0;
  dragging.classList.remove("dragging");
  document.removeEventListener("mousemove", moverDragNodo);
  document.removeEventListener("mouseup", terminarDragNodo);
  dragging = null;
}
function posicionarEnMundo(el, x, y){
  const w = parseFloat(getComputedStyle(el).width);
  const h = parseFloat(getComputedStyle(el).height);
  const maxX = mundo.clientWidth  - w;
  const maxY = mundo.clientHeight - h;
  el.style.left = Math.max(0, Math.min(x, maxX)) + "px";
  el.style.top  = Math.max(0, Math.min(y, maxY)) + "px";
}

// ======= Pan / Zoom =======
let panning=false, panStartX=0, panStartY=0, startTX=0, startTY=0;
centro.addEventListener("mousedown",(e)=>{
  if(e.ctrlKey && e.button===0){
    panning=true; panStartX=e.clientX; panStartY=e.clientY; startTX=translateX; startTY=translateY; e.preventDefault();
  }
});
document.addEventListener("mousemove",(e)=>{
  if(!panning) return;
  translateX = startTX + (e.clientX - panStartX);
  translateY = startTY + (e.clientY - panStartY);
  aplicarTransform();
});
document.addEventListener("mouseup",()=>{ panning=false; });
centro.addEventListener("wheel",(e)=>{
  if(!e.ctrlKey) return;
  e.preventDefault();
  const rect = centro.getBoundingClientRect();
  const mouseX = e.clientX - rect.left;
  const mouseY = e.clientY - rect.top;
  const worldX = (mouseX - translateX) / scale;
  const worldY = (mouseY - translateY) / scale;
  const zoomIntensity = 0.0015;
  const newScale = clamp(scale * (1 - e.deltaY * zoomIntensity), 0.2, 3.5);
  translateX = mouseX - worldX * newScale;
  translateY = mouseY - worldY * newScale;
  scale = newScale;
  aplicarTransform();
}, {passive:false});

// ======= Connections (SVG) =======
let conexionEnCurso = null; // {fromIdx, paths}
function getPortCenterWorld(portEl){
  const r = portEl.getBoundingClientRect();
  return screenToWorld(r.left + r.width/2, r.top + r.height/2);
}
function crearPathsSVG(claseExtra=""){
  const pbg = document.createElementNS("http://www.w3.org/2000/svg","path");
  const p   = document.createElementNS("http://www.w3.org/2000/svg","path");
  const g   = document.createElementNS("http://www.w3.org/2000/svg","path");
  pbg.setAttribute("class", `edge-path bg ${claseExtra}`);
  p.setAttribute("class", `edge-path ${claseExtra}`);
  g.setAttribute("class", `edge-path glow ${claseExtra}`);
  edgesSvg.appendChild(g); edgesSvg.appendChild(pbg); edgesSvg.appendChild(p);
  return {pathBg:pbg, path:p, glow:g};
}
function makePathD(x1,y1,x2,y2){
  const dx = Math.max(40, Math.abs(x2-x1)*0.5);
  return `M ${x1} ${y1} C ${x1+dx} ${y1}, ${x2-dx} ${y2}, ${x2} ${y2}`;
}
function drawPaths(paths, x1,y1,x2,y2){
  const d = makePathD(x1,y1,x2,y2);
  paths.pathBg.setAttribute("d", d);
  paths.path.setAttribute("d", d);
  paths.glow.setAttribute("d", d);
}
function iniciarConexionDesdeSalida(e, nodoEl, portOut){
  const fromIdx = parseInt(nodoEl.dataset.index,10);
  const a = getPortCenterWorld(portOut);
  const paths = crearPathsSVG("preview");
  conexionEnCurso = { fromIdx, paths };
  document.querySelectorAll('.port.in').forEach(p=>p.classList.add('highlight'));
  const move = (ev)=>{ const w = screenToWorld(ev.clientX, ev.clientY); drawPaths(paths, a.x, a.y, w.x, w.y); };
  const up = ()=>{ cancelarPreview(); document.removeEventListener('mousemove', move); document.removeEventListener('mouseup', up); };
  document.addEventListener('mousemove', move); document.addEventListener('mouseup', up);
}
function finalizarConexionEnEntrada(targetNodoEl, portIn){
  if(!conexionEnCurso) return;
  const toIdx = parseInt(targetNodoEl.dataset.index,10);
  if(conexionEnCurso.fromIdx === toIdx){ cancelarPreview(); return; }
  const fromEl = nodos[conexionEnCurso.fromIdx].el;
  const portOut = fromEl.querySelector('.port.out');
  const a = getPortCenterWorld(portOut);
  const b = getPortCenterWorld(portIn);
  const paths = crearPathsSVG();
  drawPaths(paths, a.x, a.y, b.x, b.y);
  conexiones.push({ from: conexionEnCurso.fromIdx, to: toIdx, ...paths });
  cancelarPreview();
}
function cancelarPreview(){
  if(!conexionEnCurso) return;
  document.querySelectorAll('.port.in').forEach(p=>p.classList.remove('highlight'));
  const {paths} = conexionEnCurso;
  [paths.path, paths.pathBg, paths.glow].forEach(el=> el.remove());
  conexionEnCurso = null;
}
function actualizarConexionesDeNodo(idx){
  conexiones.forEach(con=>{
    if(con.from===idx || con.to===idx){
      const fromEl = nodos[con.from].el.querySelector('.port.out');
      const toEl   = nodos[con.to].el.querySelector('.port.in');
      const a = getPortCenterWorld(fromEl);
      const b = getPortCenterWorld(toEl);
      drawPaths(con, a.x, a.y, b.x, b.y);
    }
  });
}

// ======= Execute Graph (Play) =======
playBtn.addEventListener("click", async ()=>{
  // Leer config de cada nodo
  nodos.forEach(n=>{
    n.config = {};
    if(n.type === "list_files"){
      const input = n.el.querySelector(".body input");
      n.config.path = input ? input.value.trim() : "";
    }
  });

  const nodesPayload = nodos.map(n=>({ id:n.id, type:n.type, config:n.config }));
  const edgesPayload = conexiones.map(c=>({ from: nodos[c.from].id, to: nodos[c.to].id }));

  log("Ejecutando grafo…");
  const res = await fetch("/api/execute", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({ nodes: nodesPayload, edges: edgesPayload })
  }).then(r=>r.json()).catch(err=>({error:String(err)}));

  if(res.error){ log("ERROR: "+res.error); return; }
  const results = res.results || {};
  Object.entries(results).forEach(([nid, r])=>{
    const node = nodos.find(n=>n.id===nid);
    if(!node) return;
    if(r.ok){
      log(`✔ ${node.type} (${nid}) OK`);
      if(node.type === "list_files"){
        const body = node.el.querySelector(".body");
        const out = document.createElement("div");
        out.style.font = "12px ui-monospace";
        out.style.maxHeight = "56px";
        out.style.overflow = "auto";
        const names = (r.data.files||[]).slice(0,6).map(f => (f.is_dir ? "📁 " : "📄 ") + f.name);
        out.textContent = names.join("\n") + ((r.data.files||[]).length>6 ? "\n…" : "");
        body.appendChild(out);
      }
    } else {
      log(`✖ ${node.type} (${nid}) ERROR: ${r.error}`);
    }
  });
});
