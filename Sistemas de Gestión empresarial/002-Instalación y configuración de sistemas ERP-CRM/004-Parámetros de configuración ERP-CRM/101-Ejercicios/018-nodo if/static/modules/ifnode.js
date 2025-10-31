// static/modules/ifnode.js
export default {
  type: "ifnode",

  buildBody(el, toolSpec, nodeId) {
    const body = el.querySelector(".body");
    const def = toolSpec?.config?.expr?.default ?? "bool(x)";
    body.innerHTML = `
      <div class="form-row">
        <label for="expr_${nodeId}">Expresión (Python) con <code>x</code></label>
        <input id="expr_${nodeId}" type="text" value="${def}" placeholder="p.ej: x>10, 'ok' in x">
      </div>
    `;

    // Añadimos dos salidas: true/false (data-port = 'true' / 'false')
    const outTrue  = document.createElement("div");
    const outFalse = document.createElement("div");
    outTrue.className  = "port out";  outTrue.dataset.port  = "true";  outTrue.title  = "Salida TRUE";
    outFalse.className = "port out";  outFalse.dataset.port = "false"; outFalse.title = "Salida FALSE";
    outTrue.style.top = "35%";  outFalse.style.top = "65%";
    el.appendChild(outTrue);
    el.appendChild(outFalse);

    return true;
  },

  readConfig(el) {
    const expr = el.querySelector(".body input")?.value?.trim() || "bool(x)";
    return { expr };
  },

  renderResult(el, data) {
    const b = el.querySelector(".body");
    const div = document.createElement("div");
    div.style.font = "12px ui-monospace";
    const branch = data?.meta?.branch || "?";
    const err = data?.meta?.error;
    div.textContent = `branch: ${branch}` + (err ? ` | error: ${err}` : "");
    b.appendChild(div);
  }
};
