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
      main table{width:100%;border:3px solid var(--color_primario);border-collapse:collapse;}
      main table tr:nth-child(even){background:white;}
      main table td{padding:calc(var(--margen)/2);}
      main table th{background:var(--color_primario);padding:calc(var(--margen)/2);color:aliceblue;}
      .activo{width:105%;}
    </style>
  </head>
  <body>
    <nav>
      <?php // Listado de los botones en base a las tablas de la base de datos
        $resultado = mysqli_query($conexion, "SHOW TABLES;");
        while($fila = mysqli_fetch_assoc($resultado)){
        if($fila['Tables_in_empresarial'] == $_GET['tabla']){$clase = "activo";}else{$clase = "";}
        echo "<a class='".$clase."' href='?tabla=".$fila['Tables_in_empresarial']."'>".$fila['Tables_in_empresarial']."</a>";}
      ?>
    </nav>
    <main>
      <table>
      <?php // Listado de la tabla actualmente seleccionada
        $resultado = mysqli_query($conexion, "SELECT * FROM ".$_GET['tabla'].";");$contador=0;
        while($fila = mysqli_fetch_assoc($resultado)){
          if($contador == 0){echo "<tr>";foreach($fila as $clave=>$valor){echo "<th>".$clave."</th>";}echo "</tr>";}
          echo "<tr>";foreach($fila as $clave=>$valor){echo "<td>".$valor."</td>";}echo "</tr>";$contador++;
        }
      ?>
      </table>
    </main>
  </body>
</html>
