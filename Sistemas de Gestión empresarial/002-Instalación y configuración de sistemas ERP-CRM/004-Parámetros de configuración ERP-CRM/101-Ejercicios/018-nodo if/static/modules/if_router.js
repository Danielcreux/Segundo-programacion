export default {
  type: "if_router",
  buildBody(el) {
    const body = el.querySelector(".body");
    body.innerHTML = `
      <div class="muted" style="font-size:12px">
        Entradas: cond (bool) y payload (cualquier dato).<br>
        Salidas: <code>true</code> y <code>false</code>.
      </div>
    `;
    // Añadimos dos salidas con nombre (ya existe "default", lo quitamos si quedara)
    el.querySelectorAll('.port.out').forEach(p=>p.remove());
    // Crear dos salidas nombradas:
    const make = (name, title)=>{
      const p = document.createElement('div');
      p.className = 'port out';
      p.dataset.port = name;
      p.title = title;
      el.appendChild(p);
      p.addEventListener('mousedown',(e)=>{ e.stopPropagation(); iniciarConexionDesdeSalida(e, el, p); });
      return p;
    };
    make("true", "Salida rama TRUE").style.top  = "30%";
    make("false","Salida rama FALSE").style.top = "70%";
  },
  readConfig(){ return {}; },
  renderResult(el, data){
    const body = el.querySelector(".body");
    const pre = document.createElement("div");
    pre.style.font="12px ui-monospace"; pre.style.marginTop="6px";
    pre.textContent = `cond: ${data?.result === true ? "true" : "false"}`;
    body.appendChild(pre);
  }
};
