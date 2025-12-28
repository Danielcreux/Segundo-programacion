<?php $conexion = mysqli_connect("localhost","usuarioempresarial","usuarioempresarial","empresarial"); ?>

<!doctype html>
<html lang="es">
  <head><title>microERP</title><meta charset="utf-8">
    <style>
      :root{--margen: 20px;--color_primario: indigo;}
      html,body{width:100%;height:100%;padding:0px;margin:0px;}
      body{display:flex;}
      nav{background:indigo;flex:1;padding:var(--margen);display:flex;flex-direction:column;gap:var(--margen);}
      main{background:aliceblue;flex:6;padding:var(--margen);}
    </style>
  </head>
  <body>
    <nav>
      <?php
        $resultado = mysqli_query($conexion, "SHOW TABLES;");
      ?>
    </nav>
    <main>
    </main>
  </body>
</html>