// static/modules/copiarencarpeta.js
export default {
  type: "copiarencarpeta",

  // Let the core build the form by schema if you want; or define custom UI:
  buildBody(el, toolSpec, nodeId) {
    // Custom form (one input "dest")
    const body = el.querySelector(".body");
    body.innerHTML = `
      <div class="form-row">
        <label for="dest_${nodeId}">Destination folder (within BASE_DIR)</label>
        <input id="dest_${nodeId}" type="text" value="" placeholder="e.g., out">
      </div>
      <div class="muted" style="font-size:11px">Connect an upstream node that outputs a file list (e.g., “List files in folder”).</div>
    `;
  },

  readConfig(el) {
    const dest = el.querySelector(".body input")?.value?.trim() || "";
    return { dest };
  },

  renderResult(el, data) {
    const body = el.querySelector(".body");
    const div = document.createElement("div");
    div.style.font = "12px ui-monospace";
    div.style.marginTop = "6px";
    const skippedCount = (data.skipped || []).length;
    div.textContent = `Copied: ${data.copied} → ${data.dest}` + (skippedCount ? ` | Skipped: ${skippedCount}` : "");
    body.appendChild(div);
  }
};
