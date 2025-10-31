// static/modules/comparar.js
export default {
  type: "comparar",

  buildBody(el, toolSpec, nodeId) {
    const body = el.querySelector(".body");
    const defOp  = toolSpec?.config?.op?.default  ?? "==";
    const defRhs = toolSpec?.config?.rhs?.default ?? "";
    body.innerHTML = `
      <div class="form-row">
        <label for="op_${nodeId}">Operador</label>
        <select id="op_${nodeId}">
          ${["<", ">", "==", "!=", "contains"].map(o => 
            `<option value="${o}" ${o===defOp?"selected":""}>${o}</option>`
          ).join("")}
        </select>
      </div>
      <div class="form-row">
        <label for="rhs_${nodeId}">Valor (rhs)</label>
        <input id="rhs_${nodeId}" type="text" value="${defRhs}" placeholder="comparar contra...">
      </div>
    `;
    return true;
  },

  readConfig(el) {
    const op  = el.querySelector(`#${CSS.escape(el.querySelector("select").id)}`)?.value || "==";
    const rhs = el.querySelector(".body input")?.value?.trim() ?? "";
    return { op, rhs };
  },

  renderResult(el, data) {
    const body = el.querySelector(".body");
    const tag = document.createElement("div");
    tag.style.font = "12px ui-monospace";
    tag.className = data?.data ? "status-ok" : "status-bad";
    tag.textContent = String(!!data?.data);
    body.appendChild(tag);
  }
};
