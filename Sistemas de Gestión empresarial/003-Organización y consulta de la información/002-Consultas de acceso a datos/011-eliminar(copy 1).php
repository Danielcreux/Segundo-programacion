<?php $conexion = mysqli_connect("localhost","usuarioempresarial","usuarioempresarial","empresarial"); ?>
<!doctype html>
<html lang="es">
  <head><title>microERP</title><meta charset="utf-8">
    <style>
      :root{--margen: 20px;--color_primario: indigo;--radio: 5px;}
      html,body{width:100%;height:100%;padding:0px;margin:0px;font-family:sans-serif;}
      body{display:flex;}
      nav{background:indigo;flex:1;padding:var(--margen);display:flex;flex-direction:column;gap:var(--margen);}
      nav>button{background:aliceblue;color:var(--color_primario);text-decoration:none;padding:calc(var(--margen)/2);border-radius:var(--radio);border:none;display:flex;justify-content: space-between;}
      nav button a{text-decoration:none;color:inherit;}
      main{background:aliceblue;flex:6;padding:var(--margen);}
      main table{width:100%;border:3px solid var(--color_primario);border-collapse:collapse;}
      main table tr:nth-child(even){background:white;}
      main table td{padding:calc(var(--margen)/2);}
      main table th{background:var(--color_primario);padding:calc(var(--margen)/2);color:aliceblue;}
      .activo{width:120%;}
      #corporativo{display:flex;color:white;gap:calc(var(--margen)/2);}
      #corporativo img{width:50px;}
      #corporativo p{font-size:30px;}
      .anadir{width:20px;height:20px;background:var(--color_primario);color:white;border-radius:50px;line-height:20px;font-weight:bold;position:relative;z-index:100000;animation:aparece 1s;}
      form{columns:2;gap:var(--margen);}
      form input{width:100%;padding:var(--margen);box-sizing:border-box;margin-bottom:var(--margen);border:1px solid var(--color_primario);border-radius:var(--radio);}
      form input[type=submit]{background:var(--color_primario);color:white;}
      @keyframes aparece{0%{opacity:0;transform:translateX(-30px);}100%{opacity:1;transform:translateX(0px);}}
      .eliminar{width:20px;height:20px;background:var(--color_primario);color:white;border-radius:50px;line-height:20px;font-weight:bold;position:relative;z-index:100000;display:block;text-decoration:none;text-align:center;}
      .error{background:#ffebee;color:#c62828;padding:10px;border-radius:5px;margin-bottom:10px;}
      .success{background:#e8f5e9;color:#2e7d32;padding:10px;border-radius:5px;margin-bottom:10px;}
    </style>
  </head>
  <body>
    <nav>
      <div id="corporativo"><img src="https://jocarsa.github.io/logos/logos/jocarsa%20%7C%20AliceBlue.svg"><p>jocarsa</p></div>
      <?php // Listado de los botones en base a las tablas de la base de datos
        $resultado = mysqli_query($conexion, "SHOW TABLES;");
        while($fila = mysqli_fetch_assoc($resultado)){
          // Verificar si existe $_GET['tabla'] antes de usarlo
          $tabla_actual = isset($_GET['tabla']) ? $_GET['tabla'] : '';
          $tabla_nombre = $fila['Tables_in_empresarial'];
          
          if($tabla_nombre == $tabla_actual){
            $clase = "activo";
          }else{
            $clase = "";
          }
          
          echo "<button class='".$clase."'>";
          echo "<a href='?tabla=".$tabla_nombre."'>".$tabla_nombre."</a>";
          
          if($tabla_nombre == $tabla_actual){
            echo "<a href='?operacion=añadir&tabla=".$tabla_actual."' class='anadir'>+</a>";
          }
          
          echo "</button>";
        }
      ?>
    </nav>
    <main>
      
      <?php 
        // Manejar mensajes de éxito o error
        $mensaje = '';
        $tipo_mensaje = '';
        
        // Listado de la tabla actualmente seleccionada
        if(isset($_GET['tabla']) && !empty($_GET['tabla'])){
          $tabla = $_GET['tabla'];
          
          // Verificar operación de eliminación
          if(isset($_GET['operacion']) && $_GET['operacion'] == "eliminar" && isset($_GET['id'])){
            $id = $_GET['id'];
            
            try {
              // Desactivar temporalmente las restricciones de clave foránea
              mysqli_query($conexion, "SET FOREIGN_KEY_CHECKS = 0;");
              
              // Primero eliminar registros relacionados en la tabla ventas
              // Esto aplica tanto para clientes como para productos
              if($tabla == 'clientes' || $tabla == 'productos') {
                if($tabla == 'clientes') {
                  // Eliminar ventas relacionadas con este cliente
                  mysqli_query($conexion, "DELETE FROM ventas WHERE ID_Cliente = ".$id.";");
                }
                if($tabla == 'productos') {
                  // Eliminar ventas relacionadas con este producto
                  mysqli_query($conexion, "DELETE FROM ventas WHERE ID_Producto = ".$id.";");
                }
              }
              
              // Ahora eliminar el registro principal
              $resultado_eliminar = mysqli_query($conexion, "DELETE FROM ".$tabla." WHERE Identificador = ".$id.";");
              
              // Reactivar las restricciones de clave foránea
              mysqli_query($conexion, "SET FOREIGN_KEY_CHECKS = 1;");
              
              if(mysqli_affected_rows($conexion) > 0) {
                $mensaje = "Registro eliminado correctamente.";
                $tipo_mensaje = "success";
              } else {
                $mensaje = "No se pudo eliminar el registro. Es posible que no exista o ya haya sido eliminado.";
                $tipo_mensaje = "error";
              }
              
            } catch (mysqli_sql_exception $e) {
              // Asegurarse de reactivar las restricciones si hay error
              mysqli_query($conexion, "SET FOREIGN_KEY_CHECKS = 1;");
              $mensaje = "Error: No se puede eliminar porque tiene registros relacionados en otras tablas.";
              $tipo_mensaje = "error";
            }
          }
          
          // Mostrar mensaje si existe
          if($mensaje != '') {
            echo "<div class='$tipo_mensaje'>$mensaje</div>";
          }
          
          if(isset($_GET['operacion']) && $_GET['operacion'] == "añadir"){
            echo "<form action='hola' method='POST'>";
            $resultado = mysqli_query($conexion, "SELECT * FROM ".$tabla." LIMIT 1;");
            while($fila = mysqli_fetch_assoc($resultado)){
              foreach($fila as $clave=>$valor){
                echo "<input type='text' placeholder='".$clave."'>";
              }
            }
            echo "<input type='submit'></form>";
          }else{
            echo "<table>";
            $resultado = mysqli_query($conexion, "SELECT * FROM ".$tabla.";");
            $contador = 0;
            
            while($fila = mysqli_fetch_assoc($resultado)){
              if($contador == 0){
                echo "<tr>";
                foreach($fila as $clave=>$valor){
                  echo "<th>".$clave."</th>";
                }
                echo "<th></th></tr>";
              }
              
              echo "<tr>";
              foreach($fila as $clave=>$valor){
                echo "<td>".$valor."</td>";
              }
              echo "<td><a href='?operacion=eliminar&tabla=".$tabla."&id=".$fila['Identificador']."' class='eliminar' onclick='return confirm(\"¿Estás seguro de eliminar este registro?\\n\\nAdvertencia: Si es un cliente o producto, también se eliminarán sus ventas relacionadas.\")'>x</a></td></tr>";
              $contador++;
            }
            
            echo "</table>";
          }
        } else {
          echo "<h2>Selecciona una tabla del menú izquierdo</h2>";
          echo "<p>Por favor, elige una de las tablas disponibles para ver su contenido.</p>";
        }
      ?>
      
    </main>
    <script>
      // Confirmación antes de eliminar
      document.addEventListener('DOMContentLoaded', function() {
        var linksEliminar = document.querySelectorAll('.eliminar');
        linksEliminar.forEach(function(link) {
          link.addEventListener('click', function(e) {
            if(!confirm('¿Estás seguro de que deseas eliminar este registro?\n\nAdvertencia: Si es un cliente o producto, también se eliminarán sus ventas relacionadas.')) {
              e.preventDefault();
            }
          });
        });
      });
    </script>
  </body>
</html>