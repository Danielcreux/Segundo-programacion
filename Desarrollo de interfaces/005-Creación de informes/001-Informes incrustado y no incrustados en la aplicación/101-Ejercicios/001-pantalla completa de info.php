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
      }
    </style>
  </head>
  <body>
    <?php
      for($i = 0;$i<10;$i++){
        echo '<div 
          class="tarjeta" 
          style="
            grid-column:  span '.rand(1,2).';
            grid-row:  span '.rand(1,2).';
          ">Hola</div>';
      }
    ?>
  </body>
</html>
