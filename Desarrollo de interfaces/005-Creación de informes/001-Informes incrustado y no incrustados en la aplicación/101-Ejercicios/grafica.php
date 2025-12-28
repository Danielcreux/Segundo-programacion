<?php
/**
 * grafica.php
 * Each include renders one pie chart using $pieData and optional $pieOptions.
 */

if (!isset($pieData) || !is_array($pieData)) {
    $pieData = [
        [ 'label' => 'Marketing',   'value' => rand(10,100), 'color' => '#1f235a' ],
        [ 'label' => 'Development', 'value' => rand(10,100), 'color' => '#26306b' ],
        [ 'label' => 'Support',     'value' => rand(10,100), 'color' => '#30407f' ],
        [ 'label' => 'Other',       'value' => rand(10,100), 'color' => '#3b5294' ],
    ];
}

$pieOptions = isset($pieOptions) && is_array($pieOptions) ? $pieOptions : [];

$baseId     = $pieOptions['id'] ?? uniqid('piechart_');
$width      = isset($pieOptions['width']) ? (int)$pieOptions['width'] : 300;
$showLegend = array_key_exists('showLegend', $pieOptions)
    ? (bool)$pieOptions['showLegend']
    : true;

$svgId       = $baseId . '_svg';
$legendId    = $baseId . '_legend';
$tooltipId   = $baseId . '_tooltip';
$containerId = $baseId . '_container';

$jsonOptions = JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_HEX_AMP;
$jsonData    = json_encode($pieData, $jsonOptions);

if (!defined('SVG_PIE_CHART_CSS_PRINTED')) {
    define('SVG_PIE_CHART_CSS_PRINTED', true);
    ?>
    <style>
      .svg-pie-chart-container {
        display: inline-flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        height: 100%;
        padding: 12px 16px;
        box-sizing: border-box;
        color:#e6f0ff;
      }

      .svg-pie-chart-container svg {
        flex: 1 1 auto;
        max-width: 60%;
        height: 100%;
        filter: drop-shadow(0 6px 18px rgba(0,0,0,0.7));
      }

      .svg-pie-slice {
        cursor: pointer;
        transition:
          transform 0.2s ease,
          opacity 0.2s ease,
          filter 0.2s ease;
        transform-box: fill-box;
        transform-origin: 50% 50%;
      }

      .svg-pie-slice:hover {
        transform: scale(1.06);
        opacity: 0.92;
        filter: drop-shadow(0 0 8px rgba(78,163,255,0.8));
      }

      .svg-pie-legend {
        flex: 0 0 40%;
        margin-left: 12px;
        font-size: 0.82rem;
        line-height: 1.3;
        display:flex;
        flex-direction:column;
        gap:4px;
      }

      .svg-pie-legend-item {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        padding: 3px 6px;
        border-radius: 6px;
        background: linear-gradient(
          120deg,
          rgba(10,22,60,0.7),
          rgba(20,36,90,0.3)
        );
        border:1px solid rgba(78,163,255,0.12);
      }

      .svg-pie-legend-color {
        width: 14px;
        height: 14px;
        border-radius: 3px;
        border: 1px solid rgba(0,0,0,0.35);
        box-shadow: 0 0 8px rgba(78,163,255,0.45);
      }

      .svg-pie-tooltip {
        position: fixed;
        pointer-events: none;
        padding: 0.25rem 0.55rem;
        background: radial-gradient(circle at 0 0, #4ea3ff 0, #050814 55%);
        color: #e6f0ff;
        border-radius: 4px;
        font-size: 0.78rem;
        transform: translate(-50%, -100%);
        white-space: nowrap;
        display: none;
        z-index: 9999;
        border:1px solid rgba(78,163,255,0.7);
        box-shadow: 0 6px 18px rgba(0,0,0,0.8);
      }

      @media (max-width: 1024px){
        .svg-pie-chart-container{
          flex-direction: column;
          align-items: stretch;
          justify-content: center;
          gap:8px;
        }
        .svg-pie-chart-container svg{
          max-width: 100%;
        }
        .svg-pie-legend{
          margin-left:0;
          flex: 0 0 auto;
        }
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
       aria-label="Pie chart">
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
  const data      = <?php echo $jsonData; ?>;
  const svgId     = <?php echo json_encode($svgId); ?>;
  const legendId  = <?php echo json_encode($legendId); ?>;
  const tooltipId = <?php echo json_encode($tooltipId); ?>;
  const showLegend = <?php echo $showLegend ? 'true' : 'false'; ?>;

  const svg     = document.getElementById(svgId);
  const legend  = showLegend ? document.getElementById(legendId) : null;
  const tooltip = document.getElementById(tooltipId);

  if (!svg || !tooltip) return;

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
    const end   = polarToCartesian(cx, cy, r, endAngle);
    const largeArcFlag = (endAngle - startAngle) > Math.PI ? 1 : 0;

    return [
      "M " + cx + " " + cy,
      "L " + start.x + " " + start.y,
      "A " + r + " " + r + " 0 " + largeArcFlag + " 1 " + end.x + " " + end.y,
      "Z"
    ].join(" ");
  }

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

  function renderPieChart(items) {
    clearChart();
    hideTooltip();

    const cx = 150;
    const cy = 150;
    const r  = 120;

    const total = items.reduce(function (sum, item) {
      const v = Number(item.value) || 0;
      return sum + v;
    }, 0);

    if (total === 0) {
      if (legend) {
        const msg = document.createElement("div");
        msg.textContent = "Total value is 0. Please provide positive numeric values.";
        legend.appendChild(msg);
      }
      return;
    }

    let startAngle = -Math.PI / 2;

    items.forEach(function (item, index) {
      const value = Number(item.value) || 0;
      if (value <= 0) return;

      const angle    = (value / total) * 2 * Math.PI;
      const endAngle = startAngle + angle;
      const d        = createSlicePath(cx, cy, r, startAngle, endAngle);

      const color      = item.color || fallbackColors[index % fallbackColors.length];
      const percentage = (value / total * 100);
      const label      = item.label || "";

      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", d);
      path.setAttribute("fill", color);
      path.classList.add("svg-pie-slice");
      path.dataset.label       = label;
      path.dataset.value       = value;
      path.dataset.percentage  = percentage.toFixed(1);

      path.addEventListener("mouseenter", function (evt) {
        const text = label
          ? label + ": " + value + " (" + percentage.toFixed(1) + "%)"
          : value + " (" + percentage.toFixed(1) + "%)";
        showTooltip(text, evt.clientX, evt.clientY - 10);
      });

      path.addEventListener("mousemove", function (evt) {
        tooltip.style.left = evt.clientX + "px";
        tooltip.style.top  = (evt.clientY - 10) + "px";
      });

      path.addEventListener("mouseleave", hideTooltip);

      svg.appendChild(path);

      if (legend) {
        const legendItem = document.createElement("div");
        legendItem.className = "svg-pie-legend-item";

        const colorBox = document.createElement("div");
        colorBox.className = "svg-pie-legend-color";
        colorBox.style.background = color;

        const labelSpan = document.createElement("span");
        labelSpan.textContent =
          (label || "(no label)") +
          " — " + value +
          " (" + percentage.toFixed(1) + "%)";

        legendItem.appendChild(colorBox);
        legendItem.appendChild(labelSpan);
        legend.appendChild(legendItem);
      }

      startAngle = endAngle;
    });
  }

  renderPieChart(data);
})();
</script>

