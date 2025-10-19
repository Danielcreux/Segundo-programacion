
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.jocarsaui = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /** Utility functions **/
  const normalize = (s, noDiacritics=true) =>
    noDiacritics ? s.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase() : s.toLowerCase();

  const defaultOpts = {
    placeholder: 'Escribe para filtrar…',
    keepOpenWhileTyping: true,
    closeOnSelect: true,
    minChars: 0,
    diacriticsInsensitive: true,
    status: true
  };

  /** =======================================================
   * Component: SearchableSelect
   * ======================================================= */
  class SearchableSelect {
    constructor(selectEl, options = {}) {
      if (!selectEl || selectEl.tagName !== 'SELECT') {
        throw new Error('jocarsaui.SearchableSelect: must receive a <select> element');
      }

      this.select = selectEl;
      this.opts = { ...defaultOpts, ...options };
      this.activeIndex = -1;
      this.items = [];

      this._setup();
      this._bind();
    }

    _setup() {
      // Wrap select in container
      this.root = document.createElement('div');
      this.root.className = 'jui';
      this.select.parentNode.insertBefore(this.root, this.select);
      this.root.appendChild(this.select);

      // Hide native select visually
      this.select.classList.add('jui-hidden-native');

      // Create input
      this.input = document.createElement('input');
      this.input.type = 'search';
      this.input.className = 'jui-input';
      this.input.placeholder = this.opts.placeholder;
      this.root.insertBefore(this.input, this.select.nextSibling);

      // Create panel
      this.panel = document.createElement('div');
      this.panel.className = 'jui-panel';
      this.panel.setAttribute('role', 'listbox');
      this.root.insertBefore(this.panel, this.input.nextSibling);

      // Optional status
      if (this.opts.status) {
        this.status = document.createElement('div');
        this.status.className = 'jui-status';
        this.root.appendChild(this.status);
      }

      // Extract options text
      this.allItems = Array.from(this.select.options)
        .map(o => ({ text: o.text.trim(), value: (o.value ?? o.text).trim() }))
        .filter(o => o.text && !/^--\s/.test(o.text));

      this._render(this.allItems);
    }

    _bind() {
      this.input.addEventListener('focus', () => this.open());
      this.input.addEventListener('input', () => this._filter());
      this.input.addEventListener('keydown', (e) => this._handleKeys(e));

      this.select.addEventListener('change', () => {
        const val = this.select.value || '';
        this.input.value = val;
        this._setStatus(val ? `Seleccionado: ${val}` : '');
      });

      // outside click
      document.addEventListener('click', (e) => {
        if (!this.root.contains(e.target)) this.close();
      });
    }

    _filter() {
      const q = this.input.value;
      const normQ = normalize(q, this.opts.diacriticsInsensitive);
      const list = q.length < this.opts.minChars
        ? this.allItems
        : this.allItems.filter(i => normalize(i.text, this.opts.diacriticsInsensitive).includes(normQ));
      this.activeIndex = -1;
      this._render(list);
      if (this.opts.keepOpenWhileTyping) this.open();
    }

    _handleKeys(e) {
      const items = Array.from(this.panel.querySelectorAll('.jui-item'));
      if (!items.length) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        this.activeIndex = (this.activeIndex + 1) % items.length;
        this._mark(items);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        this.activeIndex = (this.activeIndex - 1 + items.length) % items.length;
        this._mark(items);
      } else if (e.key === 'Enter') {
        if (this.activeIndex >= 0) {
          e.preventDefault();
          items[this.activeIndex].click();
        }
      } else if (e.key === 'Escape') {
        this.close();
      }
    }

    _render(list) {
      this.panel.innerHTML = '';
      if (!list.length) {
        const empty = document.createElement('div');
        empty.className = 'jui-empty';
        empty.textContent = 'Sin coincidencias';
        this.panel.appendChild(empty);
        return;
      }

      list.forEach((item) => {
        const div = document.createElement('div');
        div.className = 'jui-item';
        div.setAttribute('role', 'option');
        div.textContent = item.text;
        div.addEventListener('click', () => this._select(item));
        this.panel.appendChild(div);
      });
      this.items = list;
    }

    _select(item) {
      this.input.value = item.text;

      const found = Array.from(this.select.options).find(o => o.text.trim() === item.text);
      if (found) {
        this.select.value = found.value || found.text;
        this.select.dispatchEvent(new Event('change', { bubbles: true }));
      }

      this._setStatus(`Seleccionado: ${item.text}`);
      if (this.opts.closeOnSelect) this.close(); else this.open();
    }

    _mark(items) {
      items.forEach((el, i) => el.setAttribute('aria-selected', i === this.activeIndex ? 'true' : 'false'));
      if (this.activeIndex >= 0) items[this.activeIndex].scrollIntoView({ block: 'nearest' });
    }

    _setStatus(msg) {
      if (this.status) this.status.textContent = msg;
    }

    // Public API
    open() { this.root.classList.add('jui--open'); }
    close() { this.root.classList.remove('jui--open'); }
    focus() { this.input.focus(); }
    value() { return this.select.value; }
    destroy() {
      this.select.classList.remove('jui-hidden-native');
      this.root.parentNode.insertBefore(this.select, this.root);
      this.root.remove();
    }
  }

  /** Auto-init on data-attribute */
  function autoInit() {
    document.querySelectorAll('select[data-jui="searchable"]').forEach(sel => {
      if (!sel.__juiInstance) sel.__juiInstance = new SearchableSelect(sel);
    });
  }
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading')
      document.addEventListener('DOMContentLoaded', autoInit);
    else
      autoInit();
  }

  // Export namespace
  return { SearchableSelect };
}));

