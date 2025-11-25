(function(global){
    const NAMESPACE = 'jux';
    const NS = (name) => `${NAMESPACE}-${name}`;

    function ensureStyles(){
      const id = `${NAMESPACE}-styles`; if (document.getElementById(id)) return;
      const css = `
:root { --jux-bg:#ffffff; --jux-text:#0f172a; --jux-muted:#475569; --jux-line:#e2e8f0; --jux-chip:#f8fafc; --jux-accent:#dc143c; }
.${NS('root')} { font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,Arial; color:var(--jux-text); }
.${NS('wrap')} { max-width:1000px; margin:32px auto; padding:0 16px; }
.${NS('title')} { margin:0 0 6px; font-size:clamp(18px,3.5vw,26px); }
.${NS('subtitle')} { margin:0 0 14px; color:var(--jux-muted); }
.${NS('card')} { border:1px solid var(--jux-line); border-radius:12px; overflow:hidden; background:#fff }
.${NS('pad')} { padding:14px }
.${NS('toolbar')} { display:flex; gap:10px; align-items:center; justify-content:space-between; flex-wrap:wrap }
.${NS('badge')} { display:inline-block; background:var(--jux-chip); padding:2px 8px; border:1px solid var(--jux-line); border-radius:999px; font-size:12px; color:var(--jux-muted) }
.${NS('search')} { display:flex; gap:8px; align-items:center }
.${NS('search')} input { border:1px solid var(--jux-line); border-radius:10px; padding:8px 10px; min-width:220px }
.${NS('count')} { font-size:12px; color:var(--jux-muted) }
.${NS('scroll')} { max-height:70vh; overflow:auto; border-top:1px solid var(--jux-line) }
.${NS('table')} { width:100%; border-collapse:separate; border-spacing:0; font-size:14px }
.${NS('thead')} th { position:sticky; top:0; background:linear-gradient(0deg,#f8fafc,#ffffff); border-bottom:1px solid var(--jux-line); text-align:left; font-weight:700; padding:10px 12px; white-space:nowrap }
.${NS('th-sortable')} { cursor:pointer; user-select:none }
.${NS('th-sortable')} .${NS('dir')} { margin-left:6px; font-size:11px; color:var(--jux-muted) }
.${NS('tbody')} td { border-bottom:1px solid var(--jux-line); padding:10px 12px; vertical-align:top }
.${NS('row-odd')} { background:#fafafa }
.${NS('pagination')} { display:flex; gap:8px; align-items:center; justify-content:center; padding:16px; border-top:1px solid var(--jux-line) }
.${NS('page-btn')} { padding:6px 12px; border:1px solid var(--jux-line); border-radius:6px; background:#fff; cursor:pointer; font:inherit; transition:all 0.2s }
.${NS('page-btn')}:hover:not(:disabled) { background:var(--jux-chip) }
.${NS('page-btn')}:disabled { opacity:0.5; cursor:not-allowed }
.${NS('page-btn-active')} { background:var(--jux-text); color:#fff; border-color:var(--jux-text) }
.${NS('page-info')} { font-size:13px; color:var(--jux-muted); margin:0 8px }
.${NS('form')} { padding:20px }
.${NS('form-grid')} { display:grid; gap:20px }
.${NS('field')} { margin-bottom:0 }
.${NS('label')} { display:block; margin-bottom:6px; font-weight:600; color:var(--jux-text); font-size:13px }
.${NS('input')}, .${NS('textarea')}, .${NS('select')} { width:100%; border:1px solid var(--jux-line); border-radius:8px; padding:10px 12px; font:inherit; color:var(--jux-text); transition:border-color 0.2s }
.${NS('input')}:focus, .${NS('textarea')}:focus, .${NS('select')}:focus { outline:none; border-color:#94a3b8 }
.${NS('textarea')} { min-height:100px; resize:vertical; font-family:inherit }
.${NS('select')} { cursor:pointer }
.${NS('hint')} { display:block; margin-top:4px; font-size:12px; color:var(--jux-muted) }
.${NS('btn-group')} { display:flex; gap:10px; margin-top:24px; padding-top:20px; border-top:1px solid var(--jux-line); grid-column:1/-1 }
.${NS('btn')} { padding:10px 20px; border:1px solid var(--jux-line); border-radius:8px; font:inherit; cursor:pointer; transition:all 0.2s }
.${NS('btn-primary')} { background:var(--jux-text); color:#fff; border-color:var(--jux-text) }
.${NS('btn-primary')}:hover { background:#1e293b }
.${NS('btn-secondary')} { background:#fff; color:var(--jux-text) }
.${NS('btn-secondary')}:hover { background:var(--jux-chip) }
.${NS('charts')} { padding:20px }
.${NS('chart-grid')} { display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:24px }
.${NS('chart-item')} { text-align:center }
.${NS('chart-title')} { font-weight:600; margin-bottom:12px; color:var(--jux-text) }
.${NS('pie-chart')} { display:inline-block; position:relative }
.${NS('legend')} { margin-top:16px; text-align:left }
.${NS('legend-item')} { display:flex; align-items:center; gap:8px; margin-bottom:6px; font-size:13px }
.${NS('legend-color')} { width:16px; height:16px; border-radius:3px; flex-shrink:0 }
.${NS('legend-label')} { flex:1 }
.${NS('legend-value')} { color:var(--jux-muted); font-weight:600 }
.${NS('grid-container')} { padding:20px }
.${NS('grid-view')} { display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:20px }
.${NS('grid-card')} { border:1px solid var(--jux-line); border-radius:12px; padding:16px; background:#fff; transition:all 0.3s; cursor:pointer }
.${NS('grid-card')}:hover { box-shadow:0 4px 12px rgba(0,0,0,0.1); transform:translateY(-2px) }
.${NS('grid-card-title')} { font-weight:700; font-size:16px; margin-bottom:12px; color:var(--jux-text); border-bottom:2px solid var(--jux-line); padding-bottom:8px }
.${NS('grid-card-field')} { margin-bottom:8px; font-size:13px }
.${NS('grid-card-label')} { color:var(--jux-muted); font-weight:600; display:inline-block; min-width:100px }
.${NS('grid-card-value')} { color:var(--jux-text); word-break:break-word }
.${NS('menu')} { display:flex; flex-direction:column; gap:10px; padding:20px; background:var(--jux-accent); overflow-y:auto }
.${NS('menu-header')} { color:white; margin:20px 0 10px 0; font-family:system-ui; font-size:14px; text-transform:uppercase; letter-spacing:1px; font-weight:700 }
.${NS('menu-header')}:first-child { margin-top:0 }
.${NS('menu-section')} { display:flex; flex-direction:column; gap:8px }
.${NS('menu-btn')} { background:white; width:100%; border:none; padding:10px 16px; border-radius:100px; transition:all 0.3s; border:2px solid white; cursor:pointer; font-family:system-ui; font-size:13px; font-weight:500; text-align:left }
.${NS('menu-btn')}:hover { background:var(--jux-accent); color:white }
.${NS('menu-btn-active')} { background:var(--jux-accent); color:white; border-color:white }
.${NS('menu-title')} { color:white; font-size:20px; font-weight:700; margin-bottom:16px; letter-spacing:-0.5px }
`;
      const style = document.createElement('style');
      style.id = id; style.textContent = css; document.head.appendChild(style);
    }

    const isPlain = v => Object.prototype.toString.call(v) === '[object Object]';
    
    function flatten(value, prefix=''){
      const out = {}; const stack = [{v:value,p:prefix}];
      while (stack.length){
        const {v,p} = stack.pop();
        if (Array.isArray(v)){
          const primitives = v.every(x => !isPlain(x) && !Array.isArray(x));
          if (primitives){ out[p||'value'] = v.join(', '); }
          else {
            out[p||'value'] = v.map(x => isPlain(x) ? JSON.stringify(x) : String(x)).join(', ');
          }
        } else if (isPlain(v)){
          const ks = Object.keys(v); 
          if (!ks.length){ out[p||'value'] = '{}'; continue; }
          ks.forEach(k=>{
            const nv=v[k]; 
            const np = p ? `${p}.${k}` : k;
            if (isPlain(nv)) {
              stack.push({v:nv,p:np});
            } else if (Array.isArray(nv)) {
              const primitives = nv.every(x => !isPlain(x) && !Array.isArray(x));
              out[np] = primitives ? nv.join(', ') : nv.map(x => isPlain(x) ? JSON.stringify(x) : String(x)).join(', ');
            } else {
              out[np] = nv==null ? '' : String(nv);
            }
          });
        } else { 
          out[p||'value'] = v==null ? '' : String(v); 
        }
      }
      return out;
    }
    
    function normalizeTop(json){ 
      if (Array.isArray(json)) return json; 
      if (isPlain(json)){ 
        const key=Object.keys(json).find(k=>Array.isArray(json[k])); 
        return key?json[key]:[json]; 
      } 
      return [json]; 
    }
    
    const collectColumns = rows => Array.from(rows.reduce((s,r)=>{ Object.keys(r).forEach(k=>s.add(k)); return s; }, new Set()));

    function analyzeField(values){
      const nonEmpty = values.filter(v => v != null && v !== '');
      if (!nonEmpty.length) return { type: 'text' };

      const allNumeric = nonEmpty.every(v => !isNaN(Number(v)));
      if (allNumeric) return { type: 'number' };

      const strings = nonEmpty.map(v => String(v));
      const unique = [...new Set(strings)];
      const repetitionRatio = unique.length / strings.length;
      if (repetitionRatio < 0.5 && unique.length > 1 && unique.length < 20) {
        return { type: 'select', options: unique.sort() };
      }

      const avgLength = strings.reduce((sum, s) => sum + s.length, 0) / strings.length;
      if (avgLength > 80) {
        return { type: 'textarea' };
      }

      return { type: 'text' };
    }

    function analyzeForChart(values){
      const nonEmpty = values.filter(v => v != null && v !== '');
      if (!nonEmpty.length) return null;

      const strings = nonEmpty.map(v => String(v));
      const unique = [...new Set(strings)];
      
      if (unique.length === strings.length || unique.length > 12) return null;

      const counts = {};
      strings.forEach(v => counts[v] = (counts[v] || 0) + 1);
      
      return { counts, total: strings.length };
    }

    const CHART_COLORS = [
      '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
      '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
      '#14b8a6', '#a855f7'
    ];

    function createPieChart(data, title){
      const total = data.total;
      const entries = Object.entries(data.counts).sort((a,b) => b[1] - a[1]);
      
      const size = 200;
      const radius = 80;
      const centerX = size / 2;
      const centerY = size / 2;

      let currentAngle = -90;
      const slices = entries.map(([label, count], idx) => {
        const percent = count / total;
        const angle = percent * 360;
        const startAngle = currentAngle;
        const endAngle = currentAngle + angle;
        currentAngle = endAngle;

        const startRad = (startAngle * Math.PI) / 180;
        const endRad = (endAngle * Math.PI) / 180;

        const x1 = centerX + radius * Math.cos(startRad);
        const y1 = centerY + radius * Math.sin(startRad);
        const x2 = centerX + radius * Math.cos(endRad);
        const y2 = centerY + radius * Math.sin(endRad);

        const largeArc = angle > 180 ? 1 : 0;
        const path = `M ${centerX} ${centerY} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;

        return {
          path,
          color: CHART_COLORS[idx % CHART_COLORS.length],
          label,
          count,
          percent: (percent * 100).toFixed(1)
        };
      });

      const svg = `<svg viewBox="0 0 ${size} ${size}" width="${size}" height="${size}">${slices.map(s => `<path d="${s.path}" fill="${s.color}" stroke="#fff" stroke-width="2"/>`).join('')}</svg>`;

      return { svg, slices, title };
    }

    class JocarsaUX {
      constructor(){ 
        ensureStyles(); 
        this.state={ 
          columns:[], rows:[], view:[], sort:{key:null, dir:1}, query:'',
          page: 1, rowsPerPage: 10
        }; 
        this._els={ host:null, table:null, thead:null, tbody:null, search:null, count:null, pagination:null }; 
      }

      menuRenderer({ target, sections=[], title='Menu', onItemClick=null, color='#dc143c' }={}){
        const host = (typeof target==='string') ? document.querySelector(target) : target; 
        if (!host) throw new Error('Target not found');
        
        host.classList.add(NS('menu'));
        host.style.background = color;
        host.innerHTML = '';

        if (title) {
          const titleEl = el('div', NS('menu-title'), title);
          host.appendChild(titleEl);
        }

        sections.forEach(section => {
          if (section.header) {
            const header = el('h3', NS('menu-header'), section.header);
            host.appendChild(header);
          }

          const sectionDiv = el('div', NS('menu-section'));
          
          if (section.items && Array.isArray(section.items)) {
            section.items.forEach(item => {
              const btn = el('button', NS('menu-btn'), item.label || item);
              
              if (item.active) {
                btn.classList.add(NS('menu-btn-active'));
              }
              
              btn.onclick = () => {
                const allBtns = host.querySelectorAll(`.${NS('menu-btn')}`);
                allBtns.forEach(b => b.classList.remove(NS('menu-btn-active')));
                btn.classList.add(NS('menu-btn-active'));
                
                if (onItemClick) {
                  onItemClick(item.value !== undefined ? item.value : item.label || item, item);
                } else if (item.onClick) {
                  item.onClick(item);
                }
              };
              
              sectionDiv.appendChild(btn);
            });
          }
          
          host.appendChild(sectionDiv);
        });

        return this;
      }

      gridRenderer({ target, data, flattenObjects=true, title='jocarsa|ux', subtitle='Grid card view', cardsPerPage=9, titleField=null, onCardClick=null }={}){
        const host = (typeof target==='string') ? document.querySelector(target) : target; 
        if (!host) throw new Error('Target not found');
        this._els.host = host;
        host.classList.add(NS('root'));
        host.innerHTML = '';

        const wrap = el('div', NS('wrap'));
        const h1 = el('h1', NS('title'), title);
        const p = el('p', NS('subtitle'), subtitle);
        const card = el('div', NS('card'));
        const pad = el('div', NS('pad'));
        const toolbar = el('div', NS('toolbar'));
        const badge = el('span', NS('badge'), 'Grid view');
        const searchBox = el('div', NS('search'));
        const label = el('label', null, 'Search'); label.htmlFor = NS('search-input');
        const input = el('input'); input.id = NS('search-input');
        const count = el('span', NS('count'));
        searchBox.append(label, input, count);
        toolbar.append(badge, searchBox);
        pad.append(toolbar);

        const gridContainer = el('div', NS('grid-container'));
        const gridView = el('div', NS('grid-view'));
        gridContainer.appendChild(gridView);

        const paginationDiv = el('div', NS('pagination'));
        
        card.append(pad, gridContainer, paginationDiv);
        wrap.append(h1, p, card);
        host.append(wrap);

        this._els = { host, gridView, search: input, count, pagination: paginationDiv };

        const arr = normalizeTop(data);
        const flat = flattenObjects ? arr.map(obj => flatten(obj)) : arr;
        this.state.columns = collectColumns(flat);
        this.state.rows = flat; 
        this.state.view = flat.slice(); 
        this.state.query='';
        this.state.page = 1;
        this.state.rowsPerPage = cardsPerPage;
        this.state.titleField = titleField || this.state.columns[0];
        this.state.onCardClick = onCardClick;

        input.value = '';
        input.oninput = () => this.setGridFilter(input.value);

        this._renderGrid();
        this._renderGridPagination();
        return this;
      }

      setGridFilter(query=''){
        this.state.query = String(query).toLowerCase();
        const { rows, columns } = this.state;
        if (!this.state.query) this.state.view = rows.slice();
        else this.state.view = rows.filter(r=>columns.some(k=>{ const v=r[k]; return v && String(v).toLowerCase().includes(this.state.query); }));
        this.state.page = 1;
        this._renderGrid();
        this._renderGridPagination();
        return this;
      }

      _renderGrid(){
        const { columns, view, page, rowsPerPage, titleField, onCardClick } = this.state;
        const gridView = this._els.gridView;
        gridView.innerHTML = '';

        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        const pageData = view.slice(start, end);

        pageData.forEach((row, idx) => {
          const card = el('div', NS('grid-card'));
          
          const cardTitle = el('div', NS('grid-card-title'), row[titleField] || `Item ${start + idx + 1}`);
          card.appendChild(cardTitle);

          columns.forEach(col => {
            if (col !== titleField) {
              const fieldDiv = el('div', NS('grid-card-field'));
              const labelSpan = el('span', NS('grid-card-label'), col + ': ');
              const valueSpan = el('span', NS('grid-card-value'), row[col] || '—');
              fieldDiv.append(labelSpan, valueSpan);
              card.appendChild(fieldDiv);
            }
          });

          if (onCardClick) {
            card.onclick = () => onCardClick(row, idx);
          }

          gridView.appendChild(card);
        });

        if (this._els.count) this._els.count.textContent = `${view.length} item(s)`;
      }

      _renderGridPagination(){
        const { view, page, rowsPerPage } = this.state;
        const pagination = this._els.pagination;
        if (!pagination) return;

        pagination.innerHTML = '';
        const totalPages = Math.ceil(view.length / rowsPerPage);
        
        if (totalPages <= 1) return;

        const prevBtn = el('button', NS('page-btn'), '← Previous');
        prevBtn.disabled = page === 1;
        prevBtn.onclick = () => this.goToGridPage(page - 1);

        const pageInfo = el('span', NS('page-info'), `Page ${page} of ${totalPages}`);

        const pages = [];
        for (let i = 1; i <= totalPages; i++) {
          if (i === 1 || i === totalPages || (i >= page - 1 && i <= page + 1)) {
            const btn = el('button', NS('page-btn'), String(i));
            if (i === page) btn.classList.add(NS('page-btn-active'));
            btn.onclick = () => this.goToGridPage(i);
            pages.push(btn);
          } else if (pages[pages.length - 1]?.textContent !== '...') {
            pages.push(el('span', NS('page-info'), '...'));
          }
        }

        const nextBtn = el('button', NS('page-btn'), 'Next →');
        nextBtn.disabled = page === totalPages;
        nextBtn.onclick = () => this.goToGridPage(page + 1);

        pagination.append(prevBtn, ...pages, nextBtn);
      }

      goToGridPage(page){
        const totalPages = Math.ceil(this.state.view.length / this.state.rowsPerPage);
        this.state.page = Math.max(1, Math.min(page, totalPages));
        this._renderGrid();
        this._renderGridPagination();
        return this;
      }

      tableRenderer({ target, data, flattenObjects=true, title='jocarsa|ux', subtitle='Table renderer (search + sort)', rowsPerPage=10 }={}){
        const host = (typeof target==='string') ? document.querySelector(target) : target; if (!host) throw new Error('Target not found');
        this._els.host = host;
        host.classList.add(NS('root'));
        host.innerHTML = '';

        const wrap = el('div', NS('wrap'));
        const h1 = el('h1', NS('title'), title);
        const p = el('p', NS('subtitle'), subtitle);
        const card = el('div', NS('card'));
        const pad = el('div', NS('pad'));
        const toolbar = el('div', NS('toolbar'));
        const badge = el('span', NS('badge'), 'Table demo');
        const searchBox = el('div', NS('search'));
        const label = el('label', null, 'Search'); label.htmlFor = NS('search-input');
        const input = el('input'); input.id = NS('search-input');
        const count = el('span', NS('count'));
        searchBox.append(label, input, count);
        toolbar.append(badge, searchBox);
        pad.append(toolbar);

        const scroll = el('div', NS('scroll'));
        const table = el('table', NS('table'));
        const thead = document.createElement('thead'); thead.className = NS('thead');
        const tbody = document.createElement('tbody'); tbody.className = NS('tbody');
        table.append(thead, tbody);
        scroll.append(table);

        const paginationDiv = el('div', NS('pagination'));
        
        card.append(pad, scroll, paginationDiv);
        wrap.append(h1, p, card);
        host.append(wrap);

        this._els = { host, table, thead, tbody, search: input, count, pagination: paginationDiv };

        const arr = normalizeTop(data);
        const flat = flattenObjects ? arr.map(obj => flatten(obj)) : arr;
        this.state.columns = collectColumns(flat);
        this.state.rows = flat; 
        this.state.view = flat.slice(); 
        this.state.sort = {key:null, dir:1}; 
        this.state.query='';
        this.state.page = 1;
        this.state.rowsPerPage = rowsPerPage;

        input.value = '';
        input.oninput = () => this.setFilter(input.value);

        this._renderHead();
        this._renderBody();
        this._renderPagination();
        return this;
      }

            formRenderer({ 
        target, 
        data, 
        flattenObjects=true, 
        title='jocarsa|ux', 
        subtitle='Form renderer (smart input types)', 
        columns=1, 
        onSubmit=null, 
        onReset=null,
        save=null // <--- NUEVO: { table, endpoint, transform(formData), onSuccess(resp), onError(err) }
      }={}){
        const host = (typeof target==='string') ? document.querySelector(target) : target; if (!host) throw new Error('Target not found');
        this._els.host = host;
        host.classList.add(NS('root'));
        host.innerHTML = '';

        const wrap = el('div', NS('wrap'));
        const h1 = el('h1', NS('title'), title);
        const p = el('p', NS('subtitle'), subtitle);
        const card = el('div', NS('card'));

        const arr = normalizeTop(data);
        const flat = flattenObjects ? arr.map(obj => flatten(obj)) : arr;
        const cols = collectColumns(flat);

        const fieldTypes = {};
        cols.forEach(col => {
          const values = flat.map(row => row[col]);
          fieldTypes[col] = analyzeField(values);
        });

        const form = el('form', NS('form'));
        const formGrid = el('div', NS('form-grid'));
        formGrid.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;

        // Helper: '' -> null
        const toNulls = (obj) => {
          const out = {};
          Object.keys(obj).forEach(k => {
            const v = obj[k];
            out[k] = (typeof v === 'string' && v.trim() === '') ? null : v;
          });
          return out;
        };

        form.onsubmit = (e) => {
          e.preventDefault();
          const formData = {};
          cols.forEach(col => {
            const input = form.elements[col];
            if (input) formData[col] = input.value;
          });

          // Si se pasa 'save', hacemos POST al backend
          if (save && (save.table || save.endpoint)) {
            const url = save.endpoint || `/insertar/${encodeURIComponent(save.table)}`;
            const payload = save.transform ? save.transform(formData) : formData;
            const body = JSON.stringify(toNulls(payload));

            fetch(url, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
              body
            })
            .then(r => r.json().catch(() => ({})).then(j => ({ ok: r.ok, status: r.status, json: j })))
            .then(({ ok, status, json }) => {
              if (ok && !json.error) {
                if (save.onSuccess) save.onSuccess(json);
                else alert(`Insertado: ${JSON.stringify(json)}`);
              } else {
                if (save.onError) save.onError(json);
                else alert(`Error (${status}): ${json?.mensaje || 'Error al insertar'}`);
              }
            })
            .catch(err => {
              if (save.onError) save.onError(err);
              else {
                console.error(err);
                alert('Fallo de red al insertar');
              }
            });
          } else if (onSubmit) {
            onSubmit(formData); // comportamiento anterior
          } else {
            console.warn('Sin onSubmit ni save: los datos no se envían.');
          }
        };

        cols.forEach(col => {
          const fieldDiv = el('div', NS('field'));
          const label = el('label', NS('label'), col);
          label.htmlFor = `${NAMESPACE}-${col}`;

          const fieldInfo = fieldTypes[col];
          let input;

          if (fieldInfo.type === 'select') {
            input = document.createElement('select');
            input.className = NS('select');
            const emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.textContent = '-- Select --';
            input.appendChild(emptyOption);
            fieldInfo.options.forEach(opt => {
              const option = document.createElement('option');
              option.value = opt;
              option.textContent = opt;
              input.appendChild(option);
            });
            const hint = el('span', NS('hint'), `${fieldInfo.options.length} options available`);
            fieldDiv.append(label, input, hint);
          } else if (fieldInfo.type === 'textarea') {
            input = document.createElement('textarea');
            input.className = NS('textarea');
            const hint = el('span', NS('hint'), 'Long text field');
            fieldDiv.append(label, input, hint);
          } else if (fieldInfo.type === 'number') {
            input = document.createElement('input');
            input.type = 'number';
            input.className = NS('input');
            input.step = 'any';
            const hint = el('span', NS('hint'), 'Numeric field');
            fieldDiv.append(label, input, hint);
          } else {
            input = document.createElement('input');
            input.type = 'text';
            input.className = NS('input');
            const hint = el('span', NS('hint'), 'Text field');
            fieldDiv.append(label, input, hint);
          }

        input.id = `${NAMESPACE}-${col}`;
        input.name = col;
        formGrid.appendChild(fieldDiv);
        });

        const btnGroup = el('div', NS('btn-group'));
        const submitBtn = el('button', `${NS('btn')} ${NS('btn-primary')}`, 'Guardar');
        submitBtn.type = 'submit';
        const resetBtn = el('button', `${NS('btn')} ${NS('btn-secondary')}`, 'Reset');
        resetBtn.type = 'button';
        resetBtn.onclick = () => {
          form.reset();
          if (onReset) onReset();
        };
        btnGroup.append(submitBtn, resetBtn);
        formGrid.appendChild(btnGroup);
        form.appendChild(formGrid);

        card.appendChild(form);
        wrap.append(h1, p, card);
        host.append(wrap);

        return this;
      }


      chartRenderer({ target, data, flattenObjects=true, title='jocarsa|ux', subtitle='Chart renderer (auto pie charts)' }={}){
        const host = (typeof target==='string') ? document.querySelector(target) : target; if (!host) throw new Error('Target not found');
        this._els.host = host;
        host.classList.add(NS('root'));
        host.innerHTML = '';

        const wrap = el('div', NS('wrap'));
        const h1 = el('h1', NS('title'), title);
        const p = el('p', NS('subtitle'), subtitle);
        const card = el('div', NS('card'));
        const chartsDiv = el('div', NS('charts'));
        const chartGrid = el('div', NS('chart-grid'));

        const arr = normalizeTop(data);
        const flat = flattenObjects ? arr.map(obj => flatten(obj)) : arr;
        const cols = collectColumns(flat);

        let chartCount = 0;
        cols.forEach(col => {
          const values = flat.map(row => row[col]);
          const chartData = analyzeForChart(values);
          
          if (chartData) {
            const chart = createPieChart(chartData, col);
            
            const chartItem = el('div', NS('chart-item'));
            const chartTitle = el('div', NS('chart-title'), chart.title);
            const pieChart = el('div', NS('pie-chart'));
            pieChart.innerHTML = chart.svg;
            
            const legend = el('div', NS('legend'));
            chart.slices.forEach(slice => {
              const item = el('div', NS('legend-item'));
              const color = el('div', NS('legend-color'));
              color.style.backgroundColor = slice.color;
              const label = el('span', NS('legend-label'), slice.label);
              const value = el('span', NS('legend-value'), `${slice.count} (${slice.percent}%)`);
              item.append(color, label, value);
              legend.appendChild(item);
            });

            chartItem.append(chartTitle, pieChart, legend);
            chartGrid.appendChild(chartItem);
            chartCount++;
          }
        });

        if (chartCount === 0) {
          const noCharts = el('p', null, 'No chartable data found (all columns have unique values)');
          noCharts.style.padding = '20px';
          noCharts.style.color = 'var(--jux-muted)';
          noCharts.style.textAlign = 'center';
          chartsDiv.appendChild(noCharts);
        } else {
          chartsDiv.appendChild(chartGrid);
        }

        card.appendChild(chartsDiv);
        wrap.append(h1, p, card);
        host.append(wrap);

        return this;
      }

      setFilter(query=''){
        this.state.query = String(query).toLowerCase();
        const { rows, columns } = this.state;
        if (!this.state.query) this.state.view = rows.slice();
        else this.state.view = rows.filter(r=>columns.some(k=>{ const v=r[k]; return v && String(v).toLowerCase().includes(this.state.query); }));
        this.state.page = 1;
        this._renderBody();
        this._renderPagination();
        return this;
      }

      sortBy(key, dir){
        if (!key) return this;
        const s = this.state;
        if (dir == null){ if (s.sort.key === key) s.sort.dir *= -1; else { s.sort.key = key; s.sort.dir = 1; } }
        else { s.sort.key = key; s.sort.dir = dir >= 0 ? 1 : -1; }
        const d = s.sort.dir; const k = s.sort.key;
        s.view.sort((a,b)=>{
          const va=a[k] ?? '', vb=b[k] ?? '';
          const na=Number(va), nb=Number(vb);
          const bothNum = !isNaN(na) && !isNaN(nb);
          if (bothNum) return (na-nb)*d;
          return String(va).localeCompare(String(vb), undefined, {numeric:true, sensitivity:'base'})*d;
        });
        this._renderHead();
        this._renderBody();
        return this;
      }

      goToPage(page){
        const totalPages = Math.ceil(this.state.view.length / this.state.rowsPerPage);
        this.state.page = Math.max(1, Math.min(page, totalPages));
        this._renderBody();
        this._renderPagination();
        return this;
      }

      _renderHead(){
        const { columns, sort } = this.state; const thead = this._els.thead;
        thead.innerHTML = '';
        const tr = document.createElement('tr');
        columns.forEach(c=>{
          const th = document.createElement('th');
          th.className = `${NS('th-sortable')}`; th.title = `Sort by ${c}`; th.textContent = c;
          const dir = el('span', NS('dir'), sort.key===c ? (sort.dir===1 ? '▲' : '▼') : '');
          th.append(dir);
          th.addEventListener('click', ()=>this.sortBy(c));
          tr.append(th);
        });
        thead.append(tr);
      }

      _renderBody(){
        const { columns, view, page, rowsPerPage } = this.state; 
        const tbody = this._els.tbody;
        tbody.innerHTML = '';
        
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        const pageData = view.slice(start, end);
        
        const frag = document.createDocumentFragment();
        pageData.forEach((r, idx)=>{
          const tr = document.createElement('tr');
          if (idx % 2 === 0) tr.classList.add(NS('row-odd'));
          columns.forEach(c=>{
            const td = document.createElement('td');
            td.textContent = r[c] ?? '';
            tr.append(td);
          });
          frag.append(tr);
        });
        tbody.append(frag);
        if (this._els.count) this._els.count.textContent = `${view.length} row(s)`;
      }

      _renderPagination(){
        const { view, page, rowsPerPage } = this.state;
        const pagination = this._els.pagination;
        if (!pagination) return;

        pagination.innerHTML = '';
        const totalPages = Math.ceil(view.length / rowsPerPage);
        
        if (totalPages <= 1) return;

        const prevBtn = el('button', NS('page-btn'), '← Previous');
        prevBtn.disabled = page === 1;
        prevBtn.onclick = () => this.goToPage(page - 1);

        const pageInfo = el('span', NS('page-info'), `Page ${page} of ${totalPages}`);

        const pages = [];
        for (let i = 1; i <= totalPages; i++) {
          if (i === 1 || i === totalPages || (i >= page - 1 && i <= page + 1)) {
            const btn = el('button', NS('page-btn'), String(i));
            if (i === page) btn.classList.add(NS('page-btn-active'));
            btn.onclick = () => this.goToPage(i);
            pages.push(btn);
          } else if (pages[pages.length - 1]?.textContent !== '...') {
            pages.push(el('span', NS('page-info'), '...'));
          }
        }

        const nextBtn = el('button', NS('page-btn'), 'Next →');
        nextBtn.disabled = page === totalPages;
        nextBtn.onclick = () => this.goToPage(page + 1);

        pagination.append(prevBtn, ...pages, nextBtn);
      }
    }

    function el(tag, className, text){ const x=document.createElement(tag); if (className) x.className=className; if (text!=null) x.textContent=text; return x; }

    global.JocarsaUX = JocarsaUX;
    global['jocarsa|ux'] = { UX: JocarsaUX };

  })(window);
