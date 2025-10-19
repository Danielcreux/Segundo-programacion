const template = document.createElement('template');
template.innerHTML = `
  <style>
    :host {
      position: relative;
      display: inline-block;
      margin: 20px;
      font-family: system-ui, sans-serif;
    }
    button.miboton {
      padding: 6px 12px;
      border: 1px solid #ccc;
      border-radius: 6px;
      background: #f5f5f5;
      cursor: pointer;
    }
    .tooltip {
      position: absolute;
      bottom: -8px;
      right: -23px;
      background: black;
      color: white;
      padding: 5px;
      border-radius: 0px 5px 5px 5px;
      width: max-content;
      min-width: 30px;
      height: auto;
      font-size: 10px;
      text-align: center;
      line-height: 10px;
      display: none;
      pointer-events: none;
      z-index: 1;
    }
    :host(:hover) .tooltip,
    button.miboton:hover + .tooltip {
      display: block;
    }
  </style>

  <button class="miboton"></button>
  <div class="tooltip"></div>
`;

class BotonTooltip extends HTMLElement {
  static get observedAttributes() {
    return ['tooltip'];
  }

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.appendChild(template.content.cloneNode(true));
    this.button = this.shadowRoot.querySelector('button.miboton');
    this.tooltip = this.shadowRoot.querySelector('.tooltip');
  }

  connectedCallback() {
    this._updateButtonText();
    this._updateTooltip();
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (name === 'tooltip') {
      this._updateTooltip();
    }
  }

  _updateButtonText() {
    this.button.textContent = this.textContent.trim() || 'Púlsame';
  }

  _updateTooltip() {
    this.tooltip.textContent = this.getAttribute('tooltip') || 'Tooltip';
  }
}

customElements.define('boton-tooltip', BotonTooltip);

