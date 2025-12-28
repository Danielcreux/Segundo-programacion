<?php
/**
 * grafica2.php
 *
 * Expects:
 *   $pieOptions = [
 *       'id'         => 'chart_1',
 *       'width'      => 220,
 *       'showLegend' => true,
 *       'type'       => 'pie' | 'bar' | 'line',
 *       'dataUrl'    => 'data/chart1.json'   // NEW: URL del JSON externo
 *   ];
 */

// 1. Options
$pieOptions = isset($pieOptions) && is_array($pieOptions) ? $pieOptions : [];

$baseId     = $pieOptions['id'] ?? uniqid('chart_');
$width      = isset($pieOptions['width']) ? (int)$pieOptions['width'] : 220;
$showLegend = array_key_exists('showLegend', $pieOptions)
    ? (bool)$pieOptions['showLegend']
    : true;
$chartType  = isset($pieOptions['type']) ? (string)$pieOptions['type'] : 'pie';
$dataUrl    = isset($pieOptions['dataUrl']) ? (string)$pieOptions['dataUrl'] : null;

$svgId       = $baseId . '_svg';
$legendId    = $baseId . '_legend';
$tooltipId   = $baseId . '_tooltip';
$containerId = $baseId . '_container';

// 2. CSS solo una vez
if (!defined('SVG_CHARTS_CSS_PRINTED')) {
    define('SVG_CHARTS_CSS_PRINTED', true);
    ?>
    <style>
      .svg-pie-chart-container {
        display:inline-flex;
        flex-direction:row;
        align-items:center;
        justify-content:center;
        width:100%;
        height:100%;
        padding:8px 10px;
        gap:10px;
      }

      .svg-pie-chart-container svg {
        flex:0 0 auto;
        height:100%;
        filter: drop-shadow(0 0 12px rgba(59, 130, 246, 0.35)) brightness(3);
      }

      .svg-pie-slice,
      .svg-bar-rect,
      .svg-line-point {
        cursor:pointer;
        transition:transform 0.2s ease, opacity 0.2s ease, filter 0.2s ease;
        transform-box:fill-box;
        transform-origin:50% 50%;
      }

      .svg-pie-slice:hover,
      .svg-bar-rect:hover,
      .svg-line-point:hover {
        transform:scale(1.05);
        opacity:0.9;
        filter:brightness(1.2);
      }

      .svg-pie-legend {
        flex:1 1 auto;
        font-size:0.7rem;
        color:#cbd5f5;
        max-height:100%;
        overflow:hidden;
      }

      .svg-pie-legend-item {
        display:flex;
        align-items:center;
        margin-bottom:0.18rem;
        gap:0.45rem;
        white-space:nowrap;
        text-overflow:ellipsis;
        overflow:hidden;
      }

      .svg-pie-legend-color {
        width:12px;
        height:12px;
        border-radius:3px;
        border:1px solid rgba(148,163,184,0.8);
        box-shadow:0 0 8px rgba(59,130,246,0.65);
      }

      .svg-pie-legend-item span{
        opacity:0.9;
      }

      .svg-pie-tooltip {
        position:fixed;
        pointer-events:none;
        padding:0.3rem 0.5rem;
        background:radial-gradient(circle at 0 0,#22d3ee 0,#1e293b 45%);
        color:#e5e7eb;
        border-radius:6px;
        font-size:0.75rem;
        transform:translate(-50%, -120%);
        white-space:nowrap;
        display:none;
        z-index:9999;
        border:1px solid rgba(96,165,250,0.6);
        box-shadow:
          0 0 18px rgba(59,130,246,0.7),
          0 10px 25px rgba(15,23,42,0.9);
      }

      .svg-grid-lines line{
        stroke:rgba(148,163,184,0.16);
        stroke-width:0.8;
      }

      .svg-axis line{
        stroke:rgba(191,219,254,0.7);
        stroke-width:1.2;
      }

      .svg-axis-label{
        fill:#9ca3af;
        font-size:9px;
      }
    </style>
    <?php
}
?>

<div id="<?php echo htmlspecialchars($containerId, ENT_QUOTES); ?>"
     class="svg-pie-chart-container">

  <svg id="<?php echo htmlspecialchars($svgId, ENT_QUOTES); ?>"
       viewBox="0 0 300 300"
       width="<?php echo $width; ?>"
       height="<?php echo $width; ?>"
       aria-label="Chart">
  </svg>

  <?php if ($showLegend): ?>
    <div id="<?php echo htmlspecialchars($legendId, ENT_QUOTES); ?>"
         class="svg-pie-legend"
         aria-label="Legend">
    </div>
  <?php endif; ?>

  <div id="<?php echo htmlspecialchars($tooltipId, ENT_QUOTES); ?>"
       class="svg-pie-tooltip"></div>
</div>

<script>
(function () {
  const svgId      = <?php echo json_encode($svgId); ?>;
  const legendId   = <?php echo json_encode($legendId); ?>;
  const tooltipId  = <?php echo json_encode($tooltipId); ?>;
  const showLegend = <?php echo $showLegend ? 'true' : 'false'; ?>;
  const chartType  = <?php echo json_encode($chartType); ?>;
  const dataUrl    = <?php echo json_encode($dataUrl); ?>; // URL JSON externo

  const svg     = document.getElementById(svgId);
  const legend  = showLegend ? document.getElementById(legendId) : null;
  const tooltip = document.getElementById(tooltipId);

  if (!svg || !tooltip || !dataUrl) return;

  const fallbackColors = [
    "#1d4ed8","#0ea5e9","#6366f1","#22c55e",
    "#eab308","#f97316","#f43f5e","#a855f7",
    "#06b6d4","#4b5563"
  ];

  let lastRawData = null;   // última versión recibida

  function clearChart() {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    if (legend) {
      while (legend.firstChild) legend.removeChild(legend.firstChild);
    }
  }

  function showTooltip(text, x, y) {
    tooltip.textContent = text;
    tooltip.style.left  = x + "px";
    tooltip.style.top   = y + "px";
    tooltip.style.display = "block";
  }

  function hideTooltip() {
    tooltip.style.display = "none";
  }

  function attachTooltip(el, label, value, percentage) {
    if (!el) return;
    el.addEventListener("mouseenter", function (evt) {
      const text = (label || "(no label)") +
        ": " + value.toFixed(1) + " (" + percentage.toFixed(1) + "%)";
      showTooltip(text, evt.clientX, evt.clientY - 10);
    });
    el.addEventListener("mousemove", function (evt) {
      tooltip.style.left = evt.clientX + "px";
      tooltip.style.top  = (evt.clientY - 10) + "px";
    });
    el.addEventListener("mouseleave", hideTooltip);
  }

  function polarToCartesian(cx, cy, r, angleRad) {
    return {
      x: cx + r * Math.cos(angleRad),
      y: cy + r * Math.sin(angleRad)
    };
  }

  function createSlicePath(cx, cy, r, startAngle, endAngle) {
    const start = polarToCartesian(cx, cy, r, startAngle);
    const end   = polarToCartesian(cx, cy, r, endAngle);
    const largeArcFlag = (endAngle - startAngle) > Math.PI ? 1 : 0;
    return [
      "M " + cx + " " + cy,
      "L " + start.x + " " + start.y,
      "A " + r + " " + r + " 0 " + largeArcFlag + " 1 " + end.x + " " + end.y,
      "Z"
    ].join(" ");
  }

  function buildLegend(items, total) {
    if (!legend) return;
    items.forEach(function (item) {
      const value = item.value;
      const label = item.label;
      const color = item.color;
      const pct   = total > 0 ? (value / total * 100) : 0;

      const legendItem = document.createElement("div");
      legendItem.className = "svg-pie-legend-item";

      const colorBox = document.createElement("div");
      colorBox.className = "svg-pie-legend-color";
      colorBox.style.background = color;

      const labelSpan = document.createElement("span");
      labelSpan.textContent =
        (label || "(no label)") +
        " — " + value.toFixed(1) +
        " (" + pct.toFixed(1) + "%)";

      legendItem.appendChild(colorBox);
      legendItem.appendChild(labelSpan);
      legend.appendChild(legendItem);
    });
  }

  function renderPieChart(items, total) {
    const cx = 150;
    const cy = 150;
    const r  = 110;

    let startAngle = -Math.PI / 2;

    items.forEach(function (item) {
      const value = item.value;
      if (value <= 0) return;

      const angle    = (value / total) * 2 * Math.PI;
      const endAngle = startAngle + angle;
      const d        = createSlicePath(cx, cy, r, startAngle, endAngle);

      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", d);
      path.setAttribute("fill", item.color);
      path.classList.add("svg-pie-slice");

      const percentage = (value / total * 100);
      attachTooltip(path, item.label, value, percentage);

      svg.appendChild(path);
      startAngle = endAngle;
    });
  }

  function renderBarChart(items, total) {
    const chartTop    = 20;
    const chartBottom = 260;
    const chartLeft   = 40;
    const chartRight  = 280;
    const chartHeight = chartBottom - chartTop;
    const chartWidth  = chartRight - chartLeft;

    const maxValue = items.reduce(function (max, item) {
      return Math.max(max, item.value);
    }, 0);

    if (maxValue <= 0) return;

    // grid lines
    const grid = document.createElementNS("http://www.w3.org/2000/svg", "g");
    grid.setAttribute("class","svg-grid-lines");
    const steps = 4;
    for (let i = 0; i <= steps; i++) {
      const y = chartTop + (chartHeight / steps) * i;
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", chartLeft);
      line.setAttribute("y1", y);
      line.setAttribute("x2", chartRight);
      line.setAttribute("y2", y);
      grid.appendChild(line);
    }
    svg.appendChild(grid);

    // axis
    const axis = document.createElementNS("http://www.w3.org/2000/svg", "g");
    axis.setAttribute("class","svg-axis");
    const xAxis = document.createElementNS("http://www.w3.org/2000/svg", "line");
    xAxis.setAttribute("x1", chartLeft);
    xAxis.setAttribute("y1", chartBottom);
    xAxis.setAttribute("x2", chartRight);
    xAxis.setAttribute("y2", chartBottom);
    axis.appendChild(xAxis);
    svg.appendChild(axis);

    const n = items.length;
    const slotWidth = chartWidth / Math.max(n,1);
    const barWidth  = slotWidth * 0.6;

    items.forEach(function (item, index) {
      const value = item.value;
      if (value <= 0) return;

      const barHeight = (value / maxValue) * chartHeight;
      const x = chartLeft + index * slotWidth + (slotWidth - barWidth) / 2;
      const y = chartBottom - barHeight;

      const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      rect.setAttribute("x", x);
      rect.setAttribute("y", y);
      rect.setAttribute("width", barWidth);
      rect.setAttribute("height", barHeight);
      rect.setAttribute("rx", 4);
      rect.setAttribute("fill", item.color);
      rect.classList.add("svg-bar-rect");

      const percentage = (value / total * 100);
      attachTooltip(rect, item.label, value, percentage);

      svg.appendChild(rect);
    });
  }

  function renderLineChart(items, total) {
    const chartTop    = 25;
    const chartBottom = 260;
    const chartLeft   = 40;
    const chartRight  = 280;
    const chartHeight = chartBottom - chartTop;
    const chartWidth  = chartRight - chartLeft;

    const maxValue = items.reduce(function (max, item) {
      return Math.max(max, item.value);
    }, 0);

    if (maxValue <= 0) return;

    // grid
    const grid = document.createElementNS("http://www.w3.org/2000/svg", "g");
    grid.setAttribute("class","svg-grid-lines");
    const steps = 4;
    for (let i = 0; i <= steps; i++) {
      const y = chartTop + (chartHeight / steps) * i;
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", chartLeft);
      line.setAttribute("y1", y);
      line.setAttribute("x2", chartRight);
      line.setAttribute("y2", y);
      grid.appendChild(line);
    }
    svg.appendChild(grid);

    const n = items.length;
    const spacing = n > 1 ? chartWidth / (n - 1) : 0;

    let points = "";
    const lineColor = items[0] ? items[0].color : "#38bdf8";

    items.forEach(function (item, idx) {
      const value = item.value;
      const x = chartLeft + spacing * idx;
      const y = chartTop + (1 - (value / maxValue)) * chartHeight;

      points += x + "," + y + " ";

      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", x);
      circle.setAttribute("cy", y);
      circle.setAttribute("r", 4);
      circle.setAttribute("fill", item.color);
      circle.classList.add("svg-line-point");

      const percentage = (value / total * 100);
      attachTooltip(circle, item.label, value, percentage);

      svg.appendChild(circle);
    });

    const polyline = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
    polyline.setAttribute("points", points.trim());
    polyline.setAttribute("fill", "none");
    polyline.setAttribute("stroke", lineColor);
    polyline.setAttribute("stroke-width", 2);
    polyline.setAttribute("stroke-linejoin","round");
    polyline.setAttribute("stroke-linecap","round");
    svg.insertBefore(polyline, svg.firstChild);
  }

  function normalizeData(raw) {
    return raw.map(function (item, index) {
      const value = Number(item.value) || 0;
      const color = item.color || fallbackColors[index % fallbackColors.length];
      const label = item.label || "";
      return { label: label, value: value, color: color };
    });
  }

  function renderChart(raw) {
    clearChart();
    hideTooltip();

    const items = normalizeData(raw);
    const total = items.reduce(function (sum, item) {
      return sum + item.value;
    }, 0);

    if (total === 0) {
      if (legend) {
        const msg = document.createElement("div");
        msg.textContent = "Total value is 0. Please provide positive numeric values.";
        legend.appendChild(msg);
      }
      return;
    }

    if (chartType === "bar") {
      renderBarChart(items, total);
    } else if (chartType === "line") {
      renderLineChart(items, total);
    } else {
      renderPieChart(items, total);
    }

    buildLegend(items, total);
  }

  // Animación entre dos conjuntos de datos
  function animateTransition(fromRaw, toRaw, durationMs) {
    const from = normalizeData(fromRaw);
    const to   = normalizeData(toRaw);

    const maxLen = Math.max(from.length, to.length);
    const fromP = [];
    const toP   = [];

    for (let i = 0; i < maxLen; i++) {
      const f = from[i] || {
        label: to[i] ? to[i].label : "",
        value: 0,
        color: to[i] ? to[i].color : fallbackColors[i % fallbackColors.length]
      };
      const t = to[i] || {
        label: from[i] ? from[i].label : "",
        value: 0,
        color: from[i] ? from[i].color : fallbackColors[i % fallbackColors.length]
      };
      fromP.push(f);
      toP.push(t);
    }

    const start = performance.now();

    function frame(now) {
      const elapsed = now - start;
      const tNorm = Math.min(1, elapsed / durationMs);

      const current = fromP.map(function (f, i) {
        const tv = toP[i].value;
        const v = f.value + (tv - f.value) * tNorm;
        return {
          label: toP[i].label,
          value: v,
          color: toP[i].color
        };
      });

      renderChart(current);

      if (tNorm < 1) {
        requestAnimationFrame(frame);
      }
    }

    requestAnimationFrame(frame);
  }

  async function loadAndRender() {
    try {
      const response = await fetch(dataUrl + "?t=" + Date.now(), { cache: "no-store" });
      if (!response.ok) {
        console.error("Error fetching", dataUrl, response.status);
        return;
      }
      const raw = await response.json();
      if (!Array.isArray(raw)) {
        console.error("Data is not an array for", dataUrl);
        return;
      }

      if (!lastRawData) {
        // Primera carga sin animación
        lastRawData = raw;
        renderChart(raw);
      } else {
        // Animación en actualizaciones
        animateTransition(lastRawData, raw, 500); // 500 ms
        lastRawData = raw;
      }
    } catch (e) {
      console.error("Exception fetching", dataUrl, e);
    }
  }

  // Primera carga
  loadAndRender();

  // Polling cada 10 segundos
  setInterval(loadAndRender, <?php echo rand(500,2000)?>);
})();
</script>

