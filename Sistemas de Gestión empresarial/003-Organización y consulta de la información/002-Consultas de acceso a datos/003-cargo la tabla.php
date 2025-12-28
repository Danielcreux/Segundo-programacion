<?php $conexion = mysqli_connect("localhost","usuarioempresarial","usuarioempresarial","empresarial"); ?>
<!doctype html>
<html lang="es">
  <head><title>microERP</title><meta charset="utf-8">
    <style>
      :root{--margen: 20px;--color_primario: indigo;--radio: 5px;}
      html,body{width:100%;height:100%;padding:0px;margin:0px;font-family:sans-serif;}
      body{display:flex;}
      nav{background:indigo;flex:1;padding:var(--margen);display:flex;flex-direction:column;gap:var(--margen);}
      nav a{background:aliceblue;color:var(--color_primario);text-decoration:none;padding:calc(var(--margen)/2);border-radius:var(--radio);}
      main{background:aliceblue;flex:6;padding:var(--margen);}
    </style>
  </head>
  <body>
    <nav>
      <?php
        $resultado = mysqli_query($conexion, "SHOW TABLES;");
        while($fila = mysqli_fetch_assoc($resultado)){echo "<a href='?tabla=".$fila['Tables_in_empresarial']."'>".$fila['Tables_in_empresarial']."</a>";}
      ?>
    </nav>
    <main>
      <table>
      <?php
        $resultado = mysqli_query($conexion, "SELECT * FROM ".$_GET['tabla'].";");
        while($fila = mysqli_fetch_assoc($resultado)){
          echo "<tr>";foreach($fila as $clave=>$valor){echo "<td>".$valor."</td>";}echo "</tr>";
        }
      ?>
      </table>
    </main>
  </body>
</html>
