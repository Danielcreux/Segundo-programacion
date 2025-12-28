<!doctype html>
<html>
  <head>
    <style>
      :root{
        --bg-main:#020712;
        --card-bg:#050b1a;
        --card-border:#1c2c4f;
        --card-glow:#3b82f6;
        --grid-gap:10px;
      }
      *{
        box-sizing:border-box;
      }
      body{
        margin:0;
        min-height:100vh;
        display:grid;
        grid-template-columns:repeat(8,1fr);
        grid-auto-rows:220px;
        grid-auto-flow:dense;
        background:
          radial-gradient(circle at 10% 20%, #0b1220 0, transparent 40%),
          radial-gradient(circle at 80% 80%, #020617 0, transparent 45%),
          var(--bg-main);
        gap:var(--grid-gap);
        padding:var(--grid-gap);
        font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
      }
      .tarjeta{
        position:relative;
        background:radial-gradient(circle at 0 0,#0b1b3a 0,#050b1a 55%);
        border-radius:10px;
        color:#e5e7eb;
        box-shadow:
          0 0 0 1px rgba(37,99,235,0.35),
          0 10px 30px rgba(15,23,42,0.9);
        display:flex;
        justify-content:center;
        align-items:center;
        overflow:hidden;
        isolation:isolate;
      }
      .tarjeta::before{
        content:"";
        position:absolute;
        inset:-40%;
        background:
          radial-gradient(circle at 0 0,rgba(56,189,248,0.15) 0,transparent 60%),
          radial-gradient(circle at 100% 100%,rgba(129,140,248,0.18) 0,transparent 60%);
        opacity:0.2;
        mix-blend-mode:screen;
        pointer-events:none;
      }
      .tarjeta::after{
        content:"";
        position:absolute;
        inset:0;
        background:
          repeating-linear-gradient(
            135deg,
            rgba(148,163,184,0.04) 0 2px,
            transparent 2px 4px
          );
        opacity:0.25;
        pointer-events:none;
      }
      .tarjeta-inner{
        position:relative;
        z-index:1;
        width:100%;
        height:100%;
        display:flex;
        align-items:center;
        justify-content:center;
      }
      .chart-label{
        position:absolute;
        top:6px;
        right:10px;
        font-size:10px;
        text-transform:uppercase;
        letter-spacing:0.12em;
        color:#9ca3af;
        background:rgba(15,23,42,0.8);
        border-radius:999px;
        padding:2px 8px;
        border:1px solid rgba(148,163,184,0.4);
        backdrop-filter:blur(4px);
        z-index:2;
      }
      @media(max-width:900px){
        body{
          grid-template-columns:repeat(2,1fr);
        }
      }
      @media(max-width:600px){
        body{
          grid-template-columns:1fr;
        }
      }
    </style>
  </head>
  <body>
    <?php
      // Example: array of JSON strings for each chart
      $jsonCharts = [

        // 1
        '[
          {"label": "Alpha",   "value": 45, "color": "#0a1a3c"},
          {"label": "Beta",    "value": 25, "color": "#10244d"},
          {"label": "Gamma",   "value": 20, "color": "#1a3366"},
          {"label": "Delta",   "value": 10, "color": "#244280"}
        ]',

        // 2
        '[
          {"label": "North",   "value": 35, "color": "#0d1f44"},
          {"label": "South",   "value": 30, "color": "#132a58"},
          {"label": "East",    "value": 20, "color": "#1e3b73"},
          {"label": "West",    "value": 15, "color": "#294c8f"}
        ]',

        // 3
        '[
          {"label": "Red",     "value": 50, "color": "#0a1330"},
          {"label": "Green",   "value": 20, "color": "#142047"},
          {"label": "Blue",    "value": 15, "color": "#1f2e5e"},
          {"label": "Yellow",  "value": 15, "color": "#2b3d7a"}
        ]',

        // 4
        '[
          {"label": "Jan",     "value": 30, "color": "#0c1638"},
          {"label": "Feb",     "value": 30, "color": "#14224c"},
          {"label": "Mar",     "value": 25, "color": "#1d3062"},
          {"label": "Apr",     "value": 15, "color": "#2a437f"}
        ]',

        // 5
        '[
          {"label": "Chrome",  "value": 40, "color": "#09122c"},
          {"label": "Firefox", "value": 20, "color": "#111d40"},
          {"label": "Edge",    "value": 20, "color": "#1b2d59"},
          {"label": "Safari",  "value": 20, "color": "#274173"}
        ]',

        // 6
        '[
          {"label": "CPU",     "value": 55, "color": "#0a1a3c"},
          {"label": "GPU",     "value": 25, "color": "#132a58"},
          {"label": "RAM",     "value": 10, "color": "#1f3c74"},
          {"label": "Disk",    "value": 10, "color": "#2b4e8f"}
        ]',

        // 7
        '[
          {"label": "Spain",   "value": 30, "color": "#0d1f44"},
          {"label": "France",  "value": 30, "color": "#162b58"},
          {"label": "Italy",   "value": 20, "color": "#1f386f"},
          {"label": "Germany", "value": 20, "color": "#2a4788"}
        ]',

        // 8
        '[
          {"label": "Sales",       "value": 60, "color": "#0a1534"},
          {"label": "Purchasing",  "value": 20, "color": "#121f48"},
          {"label": "Logistics",   "value": 10, "color": "#1c2b61"},
          {"label": "Warehouse",   "value": 10, "color": "#283c7e"}
        ]',

        // 9
        '[
          {"label": "Facebook",    "value": 25, "color": "#09122c"},
          {"label": "Instagram",   "value": 35, "color": "#17244d"},
          {"label": "YouTube",     "value": 20, "color": "#233666"},
          {"label": "TikTok",      "value": 20, "color": "#2f4882"}
        ]',

        // 10
        '[
          {"label": "X",       "value": 30, "color": "#0b1736"},
          {"label": "Y",       "value": 30, "color": "#13234a"},
          {"label": "Z",       "value": 20, "color": "#1c315f"},
          {"label": "W",       "value": 20, "color": "#28427c"}
        ]',
      ];

      $chartTypes = ['pie','bar','line'];

      for ($i = 0; $i < 10; $i++) {

        $jsonForThisCard = $jsonCharts[$i % count($jsonCharts)];
        $pieData = json_decode($jsonForThisCard, true);

        // random chart type
        $randomType = $chartTypes[array_rand($chartTypes)];

        $pieOptions = [
          'id'         => 'chart_' . $i,
          'width'      => 220,
          'showLegend' => true,
          'type'       => $randomType,
        ];

        echo '<div 
          class="tarjeta" 
          style="
            grid-column: span ' . rand(1,2) . ';
            grid-row: span ' . rand(1,2) . ';
          ">
          <div class="chart-label">'.strtoupper($randomType).'</div>
          <div class="tarjeta-inner">
        ';

        include "grafica2.php";

        echo '  </div>
        </div>';
      }
    ?>
  </body>
</html>

