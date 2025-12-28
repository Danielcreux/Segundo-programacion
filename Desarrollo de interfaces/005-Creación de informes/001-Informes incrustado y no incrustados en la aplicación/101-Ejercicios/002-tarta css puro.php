<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Interactive SVG Pie Chart from JSON</title>
<style>
  body {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    margin: 2rem;
    display: flex;
    gap: 2rem;
    align-items: flex-start;
  }

  #chart-container {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  svg {
    max-width: 350px;
    width: 100%;
    height: auto;
  }

  .slice {
    cursor: pointer;
    transition: transform 0.2s ease, opacity 0.2s ease;
    transform-box: fill-box;
    transform-origin: 50% 50%;
  }

  .slice:hover {
    transform: scale(1.05);
    opacity: 0.85;
  }

  #legend {
    margin-top: 1rem;
    font-size: 0.9rem;
  }

  .legend-item {
    display: flex;
    align-items: center;
    margin-bottom: 0.3rem;
    gap: 0.5rem;
  }

  .legend-color {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    border: 1px solid rgba(0,0,0,0.2);
  }

  #tooltip {
    position: fixed;
    pointer-events: none;
    padding: 0.3rem 0.5rem;
    background: rgba(0,0,0,0.8);
    color: #fff;
    border-radius: 4px;
    font-size: 0.8rem;
    transform: translate(-50%, -100%);
    white-space: nowrap;
    display: none;
    z-index: 9999;
  }

  #data-panel {
    max-width: 420px;
    width: 100%;
  }

  #data-input {
    width: 100%;
    min-height: 220px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-size: 0.85rem;
  }

  #render-btn {
    margin-top: 0.5rem;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    border: 1px solid #ccc;
    background: #f5f5f5;
    cursor: pointer;
  }

  #render-btn:hover {
    background: #e9e9e9;
  }

  #error {
    color: #b00020;
    font-size: 0.8rem;
    margin-top: 0.5rem;
    white-space: pre-wrap;
  }
</style>
</head>
<body>

<div id="chart-container">
  <svg id="pie-chart" viewBox="0 0 300 300" aria-label="Pie chart"></svg>
  <div id="legend" aria-label="Legend"></div>
</div>

<div id="data-panel">
  <p>JSON input (array of objects with <code>label</code>, <code>value</code> and optional <code>color</code>):</p>
  <textarea id="data-input">
[
  { "label": "Marketing",  "value": 40, "color": "#4e79a7" },
  { "label": "Development","value": 30, "color": "#f28e2b" },
  { "label": "Support",    "value": 20, "color": "#e15759" },
  { "label": "Other",      "value": 10, "color": "#76b7b2" }
]
  </textarea>
  <button id="render-btn">Render chart</button>
  <div id="error"></div>
</div>

<div id="tooltip"></div>

<script>
(function () {
  const svg = document.getElementById('pie-chart');
  const legend = document.getElementById('legend');
  const tooltip = document.getElementById('tooltip');
  const textarea = document.getElementById('data-input');
  const btn = document.getElementById('render-btn');
  const errorBox = document.getElementById('error');

  const fallbackColors = [
    "#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
    "#59a14f", "#edc948", "#b07aa1", "#ff9da7",
    "#9c755f", "#bab0ab"
  ];

  function polarToCartesian(cx, cy, r, angleRad) {
    return {
      x: cx + r * Math.cos(angleRad),
      y: cy + r * Math.sin(angleRad)
    };
  }

  function createSlicePath(cx, cy, r, startAngle, endAngle) {
    const start = polarToCartesian(cx, cy, r, startAngle);
    const end = polarToCartesian(cx, cy, r, endAngle);
    const largeArcFlag = (endAngle - startAngle) > Math.PI ? 1 : 0;
    const d = [
      `M ${cx} ${cy}`,
      `L ${start.x} ${start.y}`,
      `A ${r} ${r} 0 ${largeArcFlag} 1 ${end.x} ${end.y}`,
      'Z'
    ].join(' ');
    return d;
  }

  function clearChart() {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    while (legend.firstChild) legend.removeChild(legend.firstChild);
  }

  function showTooltip(text, x, y) {
    tooltip.textContent = text;
    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
    tooltip.style.display = 'block';
  }

  function hideTooltip() {
    tooltip.style.display = 'none';
  }

  function renderPieChart(data) {
    clearChart();
    hideTooltip();

    const cx = 150;
    const cy = 150;
    const r = 120;

    const total = data.reduce((sum, item) => sum + (Number(item.value) || 0), 0);
    if (total === 0) {
      errorBox.textContent = "Total value is 0. Please provide positive numeric values.";
      return;
    }

    let startAngle = -Math.PI / 2; // start at top

    data.forEach((item, index) => {
      const value = Number(item.value) || 0;
      if (value <= 0) return; // skip non-positive

      const angle = (value / total) * 2 * Math.PI;
      const endAngle = startAngle + angle;
      const d = createSlicePath(cx, cy, r, startAngle, endAngle);

      const color = item.color || fallbackColors[index % fallbackColors.length];
      const percentage = (value / total * 100);

      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', d);
      path.setAttribute('fill', color);
      path.classList.add('slice');
      path.dataset.label = item.label || '';
      path.dataset.value = value;
      path.dataset.percentage = percentage.toFixed(1);

      path.addEventListener('mouseenter', (evt) => {
        const text = `${path.dataset.label}: ${path.dataset.value} (${path.dataset.percentage}%)`;
        showTooltip(text, evt.clientX, evt.clientY - 10);
      });

      path.addEventListener('mousemove', (evt) => {
        tooltip.style.left = evt.clientX + 'px';
        tooltip.style.top = (evt.clientY - 10) + 'px';
      });

      path.addEventListener('mouseleave', hideTooltip);

      svg.appendChild(path);

      // Legend entry
      const legendItem = document.createElement('div');
      legendItem.className = 'legend-item';

      const colorBox = document.createElement('div');
      colorBox.className = 'legend-color';
      colorBox.style.background = color;

      const labelSpan = document.createElement('span');
      labelSpan.textContent = `${item.label || '(no label)'} — ${value} (${percentage.toFixed(1)}%)`;

      legendItem.appendChild(colorBox);
      legendItem.appendChild(labelSpan);
      legend.appendChild(legendItem);

      startAngle = endAngle;
    });
  }

  function renderFromTextarea() {
    errorBox.textContent = '';
    try {
      const jsonText = textarea.value.trim();
      const data = JSON.parse(jsonText);
      if (!Array.isArray(data)) {
        throw new Error("JSON must be an array of objects.");
      }
      renderPieChart(data);
    } catch (e) {
      errorBox.textContent = "JSON error: " + e.message;
      clearChart();
    }
  }

  btn.addEventListener('click', renderFromTextarea);

  // Initial render with default JSON
  renderFromTextarea();

  // Optional: expose a function to render directly from a JS JSON string or object
  window.renderPieFromJsonString = function (jsonString) {
    textarea.value = jsonString;
    renderFromTextarea();
  };
  window.renderPieFromData = function (dataArray) {
    errorBox.textContent = '';
    renderPieChart(dataArray);
  };
})();
</script>

</body>
</html>

