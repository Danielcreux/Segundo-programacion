// static/modules/listarcarpetas.js
import { openFolderPicker } from "/static/folderpicker.js";

export default {
  type: "listarcarpetas",

  buildBody(el, toolSpec, nodeId) {
    const body = el.querySelector(".body");
    const def = toolSpec?.config?.path?.default ?? "";
    body.innerHTML = `
      <div class="form-row">
        <label for="path_${nodeId}">Folder path</label>
        <div style="display:flex; gap:6px;">
          <input id="path_${nodeId}" type="text" value="${def}" placeholder="e.g., /home/user/docs" style="flex:1">
          <button type="button" class="btn btn-browse">Browse…</button>
        </div>
      </div>
    `;
    body.querySelector(".btn-browse").addEventListener("click", async ()=>{
      const current = body.querySelector("input").value.trim();
      const chosen = await openFolderPicker(current);
      if (chosen) body.querySelector("input").value = chosen;
    });
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
