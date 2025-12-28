<?php
$conexion = mysqli_connect("localhost","usuarioempresarial","usuarioempresarial","empresarial");
if(!$conexion){
  die("Error de conexión: ".mysqli_connect_error());
}

/**
 * Devuelve las claves foráneas de una tabla como:
 * [
 *   'id_cliente' => ['tabla' => 'clientes', 'columna' => 'Identificador'],
 *   ...
 * ]
 */
function obtener_claves_foraneas($conexion, $tabla, $bd = 'empresarial'){
  $fk = [];
  $sql = "
    SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = '".mysqli_real_escape_string($conexion,$bd)."'
      AND TABLE_NAME = '".mysqli_real_escape_string($conexion,$tabla)."'
      AND REFERENCED_TABLE_NAME IS NOT NULL
  ";
  $resultado = mysqli_query($conexion, $sql);
  if($resultado){
    while($fila = mysqli_fetch_assoc($resultado)){
      $fk[$fila['COLUMN_NAME']] = [
        'tabla'   => $fila['REFERENCED_TABLE_NAME'],
        'columna' => $fila['REFERENCED_COLUMN_NAME']
      ];
    }
  }
  return $fk;
}
?>
<!doctype html>
<html lang="es">
  <head>
    <title>microERP</title>
    <meta charset="utf-8">
    <style>
      :root{--margen: 20px;--color_primario: indigo;--radio: 5px;}
      html,body{width:100%;height:100%;padding:0px;margin:0px;font-family:sans-serif;}
      body{display:flex;}
      nav{background:indigo;flex:1;padding:var(--margen);display:flex;flex-direction:column;gap:var(--margen);}
      nav>button{background:aliceblue;color:var(--color_primario);text-decoration:none;padding:calc(var(--margen)/2);border-radius:var(--radio);border:none;display:flex;justify-content: space-between;align-items:center;}
      nav button a{text-decoration:none;color:inherit;}
      main{background:aliceblue;flex:6;padding:var(--margen);overflow:auto;}
      main table{width:100%;border:3px solid var(--color_primario);border-collapse:collapse;}
      main table tr:nth-child(even){background:white;}
      main table td{padding:calc(var(--margen)/2);vertical-align:top;}
      main table th{background:var(--color_primario);padding:calc(var(--margen)/2);color:aliceblue;text-align:left;}
      .activo{width:120%;}
      #corporativo{display:flex;color:white;gap:calc(var(--margen)/2);align-items:center;}
      #corporativo img{width:50px;}
      #corporativo p{font-size:30px;margin:0;}
      .anadir{width:20px;height:20px;background:var(--color_primario);color:white;border-radius:50px;line-height:20px;font-weight:bold;position:relative;z-index:100000;animation:aparece 1s;text-align:center;text-decoration:none;display:inline-block;}
      form{columns:2;gap:var(--margen);}
      form input,form select{width:100%;padding:var(--margen);box-sizing:border-box;margin-bottom:var(--margen);border:1px solid var(--color_primario);border-radius:var(--radio);}
      form input[type=submit]{background:var(--color_primario);color:white;cursor:pointer;}
      @keyframes aparece{0%{opacity:0;transform:translateX(-30px);}100%{opacity:1;transform:translateX(0px);}}
      .eliminar{width:20px;height:20px;background:var(--color_primario);color:white;border-radius:50px;line-height:20px;font-weight:bold;position:relative;z-index:100000;display:block;text-decoration:none;text-align:center;}
    </style>
  </head>
  <body>
    <nav>
      <div id="corporativo">
        <img src="https://jocarsa.github.io/logos/logos/jocarsa%20%7C%20AliceBlue.svg" alt="jocarsa">
        <p>jocarsa</p>
      </div>
      <?php
        // Listado de los botones en base a las tablas de la base de datos
        $resultado = mysqli_query($conexion, "SHOW TABLES;");
        $tabla_actual = isset($_GET['tabla']) ? $_GET['tabla'] : "";
        while($fila = mysqli_fetch_assoc($resultado)){
          $nombre_tabla = $fila['Tables_in_empresarial'];
          $clase = ($nombre_tabla == $tabla_actual) ? "activo" : "";
          echo "<button class='".$clase."'>";
            echo "<a href='?tabla=".$nombre_tabla."'>".$nombre_tabla."</a>";
            if($nombre_tabla == $tabla_actual){
              echo "<a href='?operacion=añadir&tabla=".$tabla_actual."' class='anadir'>+</a>";
            }
          echo "</button>";
        }
      ?>
    </nav>
    <main>
      <?php
        if(isset($_GET['tabla'])){
          $tabla = $_GET['tabla'];
          $foreignKeys = obtener_claves_foraneas($conexion, $tabla);

          // Eliminación
          if(isset($_GET['operacion']) && $_GET['operacion'] == "eliminar" && isset($_GET['id'])){
            mysqli_query(
              $conexion,
              "DELETE FROM ".$tabla." WHERE Identificador = ".intval($_GET['id']).";"
            );
          }

          // Inserción
          if(isset($_GET['operacion']) && $_GET['operacion'] == "añadir"){
            // Si viene por POST, procesamos inserción
            if($_SERVER['REQUEST_METHOD'] === 'POST'){
              $resultado = mysqli_query($conexion, "SELECT * FROM ".$tabla." LIMIT 1;");
              if($resultado && $fila_ejemplo = mysqli_fetch_assoc($resultado)){
                $columnas = [];
                $valores = [];
                foreach($fila_ejemplo as $clave=>$valor){
                  // Suponemos que Identificador es autoincremental
                  if($clave == 'Identificador'){ continue; }
                  if(isset($_POST[$clave]) && $_POST[$clave] !== ''){
                    $columnas[] = "`".$clave."`";
                    $valores[]  = "'".mysqli_real_escape_string($conexion,$_POST[$clave])."'";
                  }
                }
                if(count($columnas) > 0){
                  $sql_insert = "INSERT INTO ".$tabla." (".implode(",",$columnas).") VALUES (".implode(",",$valores).")";
                  mysqli_query($conexion, $sql_insert);
                }
              }
            }

            // Formulario de alta
            echo "<h2>Añadir registro en ".$tabla."</h2>";
            echo "<form action='?operacion=añadir&tabla=".$tabla."' method='POST'>";
            $resultado = mysqli_query($conexion, "SELECT * FROM ".$tabla." LIMIT 1;");
            if($resultado && $fila = mysqli_fetch_assoc($resultado)){
              foreach($fila as $clave=>$valor){
                // Omitimos el identificador
                if($clave == 'Identificador'){ continue; }

                // Si es FK: select con filas de la tabla relacionada
                if(isset($foreignKeys[$clave])){
                  $fk = $foreignKeys[$clave];
                  $tabla_fk   = $fk['tabla'];
                  $columna_fk = $fk['columna'];

                  echo "<label>".$clave."</label>";
                  echo "<select name='".$clave."'>";
                  echo "<option value=''>-- seleccionar --</option>";

                  $res_fk = mysqli_query($conexion, "SELECT * FROM ".$tabla_fk.";");
                  if($res_fk){
                    while($fila_fk = mysqli_fetch_assoc($res_fk)){
                      $partes = [];
                      foreach($fila_fk as $k2=>$v2){
                        $partes[] = $v2;
                      }
                      $texto_opcion = implode(" | ", $partes);
                      $value_opcion = $fila_fk[$columna_fk];
                      echo "<option value='".$value_opcion."'>".$texto_opcion."</option>";
                    }
                  }

                  echo "</select>";
                }else{
                  // Campo normal: input texto
                  echo "<input type='text' name='".$clave."' placeholder='".$clave."'>";
                }
              }
            }
            echo "<input type='submit' value='Guardar'>";
            echo "</form>";

          }else{
            // Listado
            echo "<h2>Listado de ".$tabla."</h2>";
            echo "<table>";
            $resultado = mysqli_query($conexion, "SELECT * FROM ".$tabla.";");
            $contador = 0;
            while($fila = mysqli_fetch_assoc($resultado)){
              if($contador == 0){
                echo "<tr>";
                  foreach($fila as $clave=>$valor){
                    echo "<th>".$clave."</th>";
                  }
                  echo "<th></th>";
                echo "</tr>";
              }

              echo "<tr>";
              foreach($fila as $clave=>$valor){
                // Si el campo es FK, mostramos fila de la tabla referenciada
                if(isset($foreignKeys[$clave]) && $valor !== null && $valor !== ''){
                  $fk = $foreignKeys[$clave];
                  $tabla_fk   = $fk['tabla'];
                  $columna_fk = $fk['columna'];

                  $sql_fk = "
                    SELECT *
                    FROM ".$tabla_fk."
                    WHERE ".$columna_fk." = '".mysqli_real_escape_string($conexion,$valor)."'
                    LIMIT 1
                  ";
                  $res_fk = mysqli_query($conexion, $sql_fk);
                  if($res_fk && $fila_fk = mysqli_fetch_assoc($res_fk)){
                    $partes = [];
                    foreach($fila_fk as $k2=>$v2){
                      $partes[] = $v2;
                    }
                    $texto_celda = implode(" | ", $partes);
                    echo "<td>".$texto_celda."</td>";
                  }else{
                    // Si no encontramos la fila referenciada, mostramos el valor bruto
                    echo "<td>".$valor."</td>";
                  }
                }else{
                  // Campo normal
                  echo "<td>".$valor."</td>";
                }
              }

              // Columna de eliminar
              echo "<td><a href='?operacion=eliminar&tabla=".$tabla."&id=".$fila['Identificador']."' class='eliminar'>x</a></td>";
              echo "</tr>";

              $contador++;
            }
            echo "</table>";
          }
        }
      ?>
    </main>
  </body>
</html>

