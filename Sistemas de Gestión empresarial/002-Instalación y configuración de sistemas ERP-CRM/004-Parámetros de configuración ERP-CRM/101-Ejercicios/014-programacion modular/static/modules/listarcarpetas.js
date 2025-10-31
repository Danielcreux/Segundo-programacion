// Módulo frontend para "listarcarpetas"
// Debe exportar por defecto un objeto con las funciones que el core puede usar.

export default {
  type: "listarcarpetas",

  // Construye/ajusta el body del nodo si quieres UI custom (opcional)
  // Si no implementas buildBody, el core genera la UI por schema.
  buildBody(el, toolSpec, nodeId) {
    // Ejemplo: nada especial, dejamos al core crear los inputs por schema
  },

  // Leer la configuración del nodo (si no está, el core lee por inputs de schema)
  readConfig(el) {
    const input = el.querySelector(".body input");
    return { path: input ? input.value.trim() : "" };
  },

  // Render de resultados tras ejecutar (opcional)
  renderResult(el, resultData) {
    const body = el.querySelector(".body");
    const out = document.createElement("div");
    out.style.font = "12px ui-monospace";
    out.style.maxHeight = "56px";
    out.style.overflow = "auto";
    const files = (resultData.files || []);
    const names = files.slice(0, 6).map(f => (f.is_dir ? "📁 " : "📄 ") + f.name);
    out.textContent = names.join("\n") + (files.length > 6 ? "\n…" : "");
    body.appendChild(out);
  }
};
