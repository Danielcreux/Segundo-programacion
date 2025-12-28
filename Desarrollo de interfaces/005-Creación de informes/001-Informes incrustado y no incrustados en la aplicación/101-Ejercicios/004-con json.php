<!doctype html>
<html>
  <head>
    <style>
      body{
        display:grid;
        grid-template-columns:repeat(4,1fr);
        background:black;
        gap:10px;
      }
      .tarjeta{
        background:MidnightBlue;
        border-radius:5px;
        padding:10px;
        height:200px;
        color:white;
        box-shadow:0px 0px 3px LightSteelBlue;
        display:flex;
        justify-content: center;
        align-items: center;
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

        // Convert JSON → PHP array that svg_pie_chart_include.php expects
        $pieData = json_decode($jsonForThisCard, true);

        // Optional: options per chart
        $pieOptions = [
          'id'         => 'chart_' . $i, // ensures unique IDs
          'width'      => 200,
          'showLegend' => true,
        ];

        echo '<div 
          class="tarjeta" 
          style="
            grid-column:  span ' . rand(1,2) . ';
            grid-row:  span ' . rand(1,2) . ';
          ">
        ';

        // Here we include your chart file (grafica.php / svg_pie_chart_include.php)
        include "grafica.php";

        echo '</div>';
      }
    ?>
  </body>
</html>

