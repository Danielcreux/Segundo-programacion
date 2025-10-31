// ====== Módulo principal (ESM) ======

// DOM
const centro   = document.getElementById("centro");
const mundo    = document.getElementById("mundo");
const edgesSvg = document.getElementById("edges");
const toolsList= document.getElementById("tools-list");
const playBtn  = document.getElementById("play");
const logEl    = document.getElementById("log");

// Estado
const nodos  = [];      // {id,x,y,el,type,config}
const conexiones = [];  // {from,to,fromPort,pathBg,path,glow}
let nodoCounter = 1;
let TOOLS = [];
const frontModules = {};  // type -> módulo JS importado

// Pan/Zoom
let scale = 1, translateX = 0, translateY = 0;
function aplicarTransform(){ mundo.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`; }
function clamp(v,a,b){ return Math.max(a, Math.min(b, v)); }
function screenToWorld(x,y){ const r=centro.getBoundingClientRect(); return { x:(x-r.left-translateX)/scale, y:(y-r.top-translateY)/scale }; }
aplicarTransform();

function log(msg){ const at=new Date().toLocaleTimeString(); logEl.textContent = `[${at}] ${msg}\n` + logEl.textContent; }

// ====== Cargar tools (y sus front-modules opcionales) ======
(async function initTools(){
  const resp = await fetch("/api/tools").then(r=>r.json());
  TOOLS = resp.tools || [];
  if(!TOOLS.length){ toolsList.innerHTML = '<div class="muted">No hay tools</div>'; return; }
  toolsList.innerHTML = "";

  // Importar dinámicamente front-modules si existen
  await Promise.all(TOOLS.map(async (t)=>{
    if(t.front_module){
      try{
        const mod = await import(t.front_module);
        if(mod?.default?.type === t.type){
          frontModules[t.type] = mod.default;
        }
      }catch(err){
        console.warn("Front module import failed:", t.type, err);
      }
    }
  }));

  // Pintar tarjetas
  TOOLS.forEach(t=>{
    const card = document.createElement("div");
    card.className="tool-card";
    card.innerHTML = `<div><strong>${t.label}</strong></div><div class="tool-desc">${t.description}</div>`;
    const btn = document.createElement("button");
    btn.className="btn-add";
    btn.textContent="Añadir como nodo";
    btn.addEventListener("click", ()=> crearNodoTool(t));
    card.appendChild(btn);
    toolsList.appendChild(card);
  });
})();

// ====== Crear nodos ======
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

// Crear un puerto de salida con nombre (y enganchar su mousedown)
function crearPuertoSalida(el, name, title){
  const p = document.createElement("div");
  p.className = "port out";
  p.dataset.port = name;  // nombre de salida
  p.title = title || ("Salida: " + name);
  el.appendChild(p);
  p.addEventListener("mousedown",(e)=>{ 
    e.stopPropagation(); 
    iniciarConexionDesdeSalida(e, el, p); 
  });
  return p;
}

function crearNodoTool(tool){
  // centro de la vista
  const rect = centro.getBoundingClientRect();
  const screenX = rect.width/2, screenY = rect.height/2;
  const nodoW = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nodo-w'));
  const nodoH = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nodo-h'));
  const worldX = (screenX - translateX) / scale - nodoW/2;
  const worldY = (screenY - translateY) / scale - nodoH/2;

  const el = crearNodoBase(Math.round(worldX), Math.round(worldY), tool.label);
  const body = el.querySelector(".body");

  // Si el módulo frontend aporta UI custom, la usamos; si no, generamos por schema
  if(frontModules[tool.type]?.buildBody){
    frontModules[tool.type].buildBody(el, tool, `n${nodoCounter}`);
  } else {
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
  }

  // Sustituimos el único out por defecto por un out nombrado "default"
  el.querySelector('.port.out')?.remove();
  crearPuertoSalida(el, "default", "Salida");

  const nodo = { id:`n${nodoCounter++}`, x:worldX, y:worldY, el, type:tool.type, config:{} };
  el.dataset.index = (nodos.length).toString();
  nodos.push(nodo);

  const portIn  = el.querySelector('.port.in');
  const handle  = el.querySelector('.drag-handle');

  handle.addEventListener("mousedown",(e)=>{ if(e.ctrlKey) return; iniciarDragNodo(e, el); });
  portIn.addEventListener("mouseup",(e)=>{ e.stopPropagation(); if(conexionEnCurso) finalizarConexionEnEntrada(el, portIn); });

  return nodo;
}

// ====== Drag de nodos ======
let dragging=null, startMouseX=0, startMouseY=0, startLeft=0, startTop=0;
function iniciarDragNodo(e, el){
  e.preventDefault();
  dragging = el; el.classList.add("dragging");
  startMouseX=e.clientX; startMouseY=e.clientY;
  startLeft=parseFloat(el.style.left)||0; startTop=parseFloat(el.style.top)||0;
  document.addEventListener("mousemove", moverDragNodo);
  document.addEventListener("mouseup", terminarDragNodo);
}
function moverDragNodo(e){
  if(!dragging) return;
  const nx = startLeft + (e.clientX - startMouseX)/scale;
  const ny = startTop  + (e.clientY - startMouseY)/scale;
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
  el.style.left = Math.max(0, Math.min(x, mundo.clientWidth  - w)) + "px";
  el.style.top  = Math.max(0, Math.min(y, mundo.clientHeight - h)) + "px";
}

// ====== Pan / Zoom ======
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

// ====== Conexiones (SVG) ======
let conexionEnCurso=null;
function getPortCenterWorld(portEl){ const r=portEl.getBoundingClientRect(); return screenToWorld(r.left+r.width/2, r.top+r.height/2); }
function crearPathsSVG(claseExtra=""){
  const pbg=document.createElementNS("http://www.w3.org/2000/svg","path");
  const p  =document.createElementNS("http://www.w3.org/2000/svg","path");
  const g  =document.createElementNS("http://www.w3.org/2000/svg","path");
  pbg.setAttribute("class",`edge-path bg ${claseExtra}`); p.setAttribute("class",`edge-path ${claseExtra}`); g.setAttribute("class",`edge-path glow ${claseExtra}`);
  edgesSvg.appendChild(g); edgesSvg.appendChild(pbg); edgesSvg.appendChild(p);
  return {pathBg:pbg, path:p, glow:g};
}
function makePathD(x1,y1,x2,y2){ const dx=Math.max(40, Math.abs(x2-x1)*0.5); return `M ${x1} ${y1} C ${x1+dx} ${y1}, ${x2-dx} ${y2}, ${x2} ${y2}`; }
function drawPaths(paths,x1,y1,x2,y2){ const d=makePathD(x1,y1,x2,y2); paths.pathBg.setAttribute("d",d); paths.path.setAttribute("d",d); paths.glow.setAttribute("d",d); }
function iniciarConexionDesdeSalida(e,nodoEl,portOut){
  const fromIdx=parseInt(nodoEl.dataset.index,10);
  const fromPort = portOut.dataset.port || "default";
  const a=getPortCenterWorld(portOut);
  const paths=crearPathsSVG("preview");
  conexionEnCurso={fromIdx, fromPort, paths};
  document.querySelectorAll('.port.in').forEach(p=>p.classList.add('highlight'));
  const move=(ev)=>{ const w=screenToWorld(ev.clientX, ev.clientY); drawPaths(paths,a.x,a.y,w.x,w.y); };
  const up=()=>{ cancelarPreview(); document.removeEventListener('mousemove',move); document.removeEventListener('mouseup',up); };
  document.addEventListener('mousemove',move); document.addEventListener('mouseup',up);
}
function finalizarConexionEnEntrada(targetNodoEl, portIn){
  if(!conexionEnCurso) return;
  const toIdx=parseInt(targetNodoEl.dataset.index,10);
  if(conexionEnCurso.fromIdx===toIdx){ cancelarPreview(); return; }
  const fromEl=nodos[conexionEnCurso.fromIdx].el;
  const portOut=fromEl.querySelector(`.port.out[data-port="${conexionEnCurso.fromPort}"]`) || fromEl.querySelector('.port.out');
  const a=getPortCenterWorld(portOut); const b=getPortCenterWorld(portIn);
  const paths=crearPathsSVG(); drawPaths(paths,a.x,a.y,b.x,b.y);
  conexiones.push({from:conexionEnCurso.fromIdx, to:toIdx, fromPort:conexionEnCurso.fromPort, ...paths}); cancelarPreview();
}
function cancelarPreview(){
  if(!conexionEnCurso) return;
  document.querySelectorAll('.port.in').forEach(p=>p.classList.remove('highlight'));
  const {paths}=conexionEnCurso; [paths.path, paths.pathBg, paths.glow].forEach(el=>el.remove()); conexionEnCurso=null;
}
function actualizarConexionesDeNodo(idx){
  conexiones.forEach(con=>{
    if(con.from===idx || con.to===idx){
      const fromEl=nodos[con.from].el.querySelector(`.port.out[data-port="${con.fromPort}"]`) || nodos[con.from].el.querySelector('.port.out');
      const toEl  =nodos[con.to].el.querySelector('.port.in');
      const a=getPortCenterWorld(fromEl); const b=getPortCenterWorld(toEl);
      drawPaths(con,a.x,a.y,b.x,b.y);
    }
  });
}

// ====== Ejecutar grafo ======
playBtn.addEventListener("click", async ()=>{
  // Leer config: si el módulo front tiene readConfig, usarla. Si no, esquema.
  nodos.forEach(n=>{
    const mod = frontModules[n.type];
    if(mod?.readConfig){
      n.config = mod.readConfig(n.el) || {};
    } else {
      n.config = {};
      const inputs = n.el.querySelectorAll(".body input");
      inputs.forEach(inp=>{
        const label = (inp.id || "").split("_").pop() || "value";
        n.config[label] = inp.value.trim();
      });
    }
  });

  const nodesPayload = nodos.map(n=>({ id:n.id, type:n.type, config:n.config }));
  const edgesPayload = conexiones.map(c=>({
    from: nodos[c.from].id,
    to:   nodos[c.to].id,
    from_port: c.fromPort || "default"
  }));

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
      const mod = frontModules[node.type];
      if(mod?.renderResult){
        mod.renderResult(node.el, r.data);
      } else {
        // fallback simple
        const body = node.el.querySelector(".body");
        const pre = document.createElement("pre");
        pre.style.maxHeight = "70px";
        pre.style.overflow = "auto";
        pre.textContent = JSON.stringify(r.data, null, 2).slice(0, 600);
        body.appendChild(pre);
      }
    } else {
      log(`✖ ${node.type} (${nid}) ERROR: ${r.error}`);
    }
  });
});
