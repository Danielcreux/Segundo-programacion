// Simple folder picker modal that browses /api/fs/list
export async function openFolderPicker(initialPath = "") {
  // Create modal
  const overlay = document.createElement("div");
  overlay.style.cssText = `
    position:fixed; inset:0; background:rgba(0,0,0,.25); display:flex; align-items:center; justify-content:center; z-index:9999;
  `;
  const modal = document.createElement("div");
  modal.style.cssText = `
    width:720px; max-height:70vh; background:#fff; border:1px solid #e5e7f0; border-radius:12px;
    box-shadow:0 20px 60px rgba(0,0,0,.25); display:flex; flex-direction:column; overflow:hidden;
    font:13px system-ui;
  `;
  modal.innerHTML = `
    <div style="padding:10px 12px; background:linear-gradient(90deg,#6aa3ff,#9c7bff); color:#fff; font-weight:600;">Select a folder</div>
    <div style="padding:8px 12px; display:flex; gap:8px; align-items:center;">
      <button data-role="up" class="btn">↑ Up</button>
      <input type="text" data-role="path" style="flex:1; padding:6px 8px; border:1px solid #cfd7ea; border-radius:8px;" />
      <button data-role="choose" class="btn">Choose this folder</button>
    </div>
    <div data-role="list" style="padding:0 12px 12px; overflow:auto; flex:1;"></div>
  `;
  overlay.appendChild(modal);
  document.body.appendChild(overlay);

  const pathInput = modal.querySelector('[data-role="path"]');
  const listEl    = modal.querySelector('[data-role="list"]');
  const upBtn     = modal.querySelector('[data-role="up"]');
  const chooseBtn = modal.querySelector('[data-role="choose"]');

  function row(html){ const d=document.createElement("div"); d.innerHTML=html; return d.firstElementChild; }

  async function loadDir(p) {
    const url = new URL("/api/fs/list", window.location.origin);
    if (p) url.searchParams.set("path", p);
    const res = await fetch(url).then(r=>r.json());
    if (res.error) throw new Error(res.error);
    pathInput.value = res.cwd;

    listEl.innerHTML = "";
    res.items.forEach(it=>{
      const el = row(`
        <div class="fp-item" style="display:flex; align-items:center; gap:8px; padding:6px 8px; border-bottom:1px solid #f1f4fb; cursor:pointer;">
          <div style="width:20px; text-align:center;">${it.is_dir ? "📁" : "📄"}</div>
          <div style="flex:1">${it.name}</div>
        </div>
      `);
      el.addEventListener("click", ()=>{
        if (it.is_dir) loadDir(it.path);
      });
      listEl.appendChild(el);
    });

    upBtn.disabled = !res.parent;
    upBtn.onclick = ()=> res.parent && loadDir(res.parent);
    chooseBtn.onclick = ()=> {
      const chosen = pathInput.value.trim();
      cleanup();
      resolve(chosen);
    };
  }

  function cleanup(){
    overlay.remove();
  }

  // Promise wrapper
  let resolve;
  const done = new Promise(r=> resolve = r);

  // Close on overlay click (optional)
  overlay.addEventListener("click", (e)=>{ if (e.target === overlay) cleanup(); });
  // ESC to close
  window.addEventListener("keydown", function esc(ev){ if(ev.key==="Escape"){ cleanup(); window.removeEventListener("keydown", esc); } });

  await loadDir(initialPath);
  return done;
}
