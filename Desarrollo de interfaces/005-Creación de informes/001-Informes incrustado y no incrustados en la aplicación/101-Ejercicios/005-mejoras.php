<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Tech Grid Dashboard</title>
    <style>
      :root{
        --bg-main: #02030a;
        --bg-panel: #091122;
        --bg-panel-alt: #101b33;
        --accent: #4ea3ff;
        --accent-soft: rgba(78,163,255,0.35);
        --text-main: #e6f0ff;
        --grid-gap: 16px;
        --card-radius: 18px;
      }

      *{
        box-sizing: border-box;
      }

      html, body{
        margin:0;
        padding:0;
        width:100%;
        height:100%;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--text-main);
      }

      body{
        display:grid;
        grid-template-columns:repeat(4,minmax(0,1fr));
        grid-auto-rows: minmax(220px, 1fr);
        grid-auto-flow: dense;
        gap:var(--grid-gap);
        padding:20px;
        background:
          radial-gradient(circle at 0% 0%, #1a2b5a 0, transparent 55%),
          radial-gradient(circle at 100% 100%, #0b142f 0, transparent 60%),
          #02030a;
        background-attachment: fixed;
        overflow:hidden;
      }

      /* subtle grid overlay */
      body::before{
        content:"";
        position:fixed;
        inset:0;
        background-image:
          linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events:none;
        opacity:0.5;
        mix-blend-mode:screen;
        z-index:-1;
      }

      .tarjeta{
        position:relative;
        background: radial-gradient(circle at 10% 0%, var(--bg-panel) 0, var(--bg-panel-alt) 55%, #050814 100%);
        border-radius:var(--card-radius);
        padding:0;
        color:var(--text-main);
        box-shadow:
          0 0 0 1px rgba(255,255,255,0.02),
          0 18px 40px rgba(0,0,0,0.7);
        display:flex;
        justify-content: center;
        align-items: stretch;
        overflow:hidden;
        transition:
          transform 0.3s ease,
          box-shadow 0.3s ease,
          border 0.3s ease,
          background 0.3s ease;
        border: 1px solid rgba(78,163,255,0.18);
      }

      /* animated highlight sweep */
      .tarjeta::before{
        content:"";
        position:absolute;
        inset:-40%;
        background:
          linear-gradient(120deg,
            transparent 0%,
            rgba(255,255,255,0.12) 45%,
            rgba(255,255,255,0.08) 50%,
            transparent 55%);
        opacity:0;
        transform: translateX(-40%);
        pointer-events:none;
      }

      .tarjeta:hover{
        transform: translateY(-4px) scale(1.02);
        box-shadow:
          0 0 0 1px rgba(78,163,255,0.25),
          0 22px 60px rgba(0,0,0,0.85);
        background: radial-gradient(circle at 15% 0%, #101f3f 0, #050814 70%);
      }

      .tarjeta:hover::before{
        opacity:1;
        animation: sweep 1.1s ease-out forwards;
      }

      @keyframes sweep{
        0%{ transform: translateX(-50%) translateY(-10%); opacity:0; }
        20%{ opacity:1; }
        100%{ transform: translateX(40%) translateY(10%); opacity:0; }
      }

      /* small screens */
      @media (max-width: 1024px){
        body{
          grid-template-columns: repeat(2, minmax(0,1fr));
          grid-auto-rows: minmax(260px, 1fr);
        }
      }

      @media (max-width: 720px){
        body{
          grid-template-columns: 1fr;
          grid-auto-rows: minmax(260px, 1fr);
          padding:12px;
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

      for ($i = 0; $i < 10; $i++) {

        // Choose one JSON per card (here we cycle through the array)
        $jsonForThisCard = $jsonCharts[$i % count($jsonCharts)];

        // Convert JSON → PHP array that grafica.php expects
        $pieData = json_decode($jsonForThisCard, true);

        // Options per chart
        $pieOptions = [
          'id'         => 'chart_' . $i, // ensures unique IDs
          'width'      => 220,
          'showLegend' => true,
        ];

        echo '<div 
          class="tarjeta" 
          style="
            grid-column:  span ' . rand(1,2) . ';
          ">
        ';

        include "grafica.php";

        echo '</div>';
      }
    ?>
  </body>
</html>

