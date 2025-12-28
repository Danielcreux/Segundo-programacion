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
        grid-template-columns:repeat(5,1fr);
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
      // 10 ficheros JSON externos
      $dataFiles = [
        "data/chart1.json",
        "data/chart2.json",
        "data/chart3.json",
        "data/chart4.json",
        "data/chart5.json",
        "data/chart6.json",
        "data/chart7.json",
        "data/chart8.json",
        "data/chart9.json",
        "data/chart10.json",
      ];

      $chartTypes = ['pie','bar','line'];

      for ($i = 0; $i < 10; $i++) {

        $randomType = $chartTypes[array_rand($chartTypes)];

        // Opciones que recibe grafica2.php
        $pieOptions = [
          'id'         => 'chart_' . $i,
          'width'      => 220,
          'showLegend' => true,
          'type'       => $randomType,
          'dataUrl'    => $dataFiles[$i], // ← fichero JSON de este gráfico
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

        include "grafica3.php";

        echo '  </div>
        </div>';
      }
    ?>
  </body>
</html>

