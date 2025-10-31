// static/modules/listarcarpetas.js
export default {
  type: "listarcarpetas",

  buildBody(el, toolSpec, nodeId) {
    const body = el.querySelector(".body");
    body.innerHTML = `
      <div class="form-row">
        <label for="path_${nodeId}">Folder path (within BASE_DIR)</label>
        <input id="path_${nodeId}" type="text" value="${toolSpec?.config?.path?.default ?? ""}" placeholder="e.g., docs">
      </div>
    `;
    // Return true to tell the core that we provided UI
    return true;
  },

  readConfig(el) {
    const path = el.querySelector(".body input")?.value?.trim() || "";
    return { path };
  },

  renderResult(el, data) {
    const body = el.querySelector(".body");
    const out = document.createElement("div");
    out.style.font = "12px ui-monospace";
    out.style.maxHeight = "56px";
    out.style.overflow = "auto";
    const files = (data.files || []);
    const names = files.slice(0, 6).map(f => (f.is_dir ? "📁 " : "📄 ") + f.name);
    out.textContent = names.join("\n") + (files.length > 6 ? "\n…" : "");
    body.appendChild(out);
  }
};
