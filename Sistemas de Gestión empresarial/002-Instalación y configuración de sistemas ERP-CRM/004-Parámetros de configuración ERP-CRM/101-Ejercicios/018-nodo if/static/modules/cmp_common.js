export function buildSimpleCompareBody(el, label, def=""){
  const body = el.querySelector(".body");
  body.innerHTML = `
    <div class="form-row">
      <label>${label}</label>
      <input type="text" value="${def}" placeholder="${label}">
    </div>
    <div class="muted" style="font-size:11px">Conecta un input a comparar. Este nodo devuelve true/false.</div>
  `;
}
export function readSimple(el){
  const v = el.querySelector("input")?.value ?? "";
  return { value: v };
}
export function renderBool(el, data){
  const body = el.querySelector(".body");
  const d = document.createElement("div");
  d.style.font="12px ui-monospace"; d.style.marginTop="6px";
  const ok = data?.result === true;
  d.innerHTML = ok ? `<span class="status-ok">true</span>` : `<span class="status-bad">false</span>`;
  body.appendChild(d);
}
