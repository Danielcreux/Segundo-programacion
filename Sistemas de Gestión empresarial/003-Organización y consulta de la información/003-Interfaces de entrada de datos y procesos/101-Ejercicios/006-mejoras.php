<?php
session_start();

// Parámetros de conexión
$db_host = "localhost";
$db_name = "tienda2526";
$db_user = "tienda2526";
$db_pass = "tienda2526";

// Credenciales iniciales
$usuario_valido     = "jocarsa";
$contrasena_valida  = "jocarsa";

$login_error = "";

// Logout
if (isset($_GET['logout'])) {
  session_unset();
  session_destroy();
  header("Location: index.php");
  exit;
}

// Login
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['accion']) && $_POST['accion'] === 'login') {
  $user = $_POST['usuario']     ?? '';
  $pass = $_POST['contrasena']  ?? '';

  if ($user === $usuario_valido && $pass === $contrasena_valida) {
    $_SESSION['usuario'] = $user;
    header("Location: index.php");
    exit;
  } else {
    $login_error = "Usuario o contraseña incorrectos";
  }
}

$logged_in = isset($_SESSION['usuario']);

// Solo conectamos a la base de datos si hay sesión iniciada
if ($logged_in) {
  $conexion = mysqli_connect($db_host, $db_user, $db_pass, $db_name);
  if(!$conexion){
    die("Error de conexión: ".mysqli_connect_error());
  }
}

/**
 * FKs salientes desde una tabla:
 * [
 *   'id_cliente' => ['tabla' => 'clientes', 'columna' => 'Identificador'],
 *   ...
 * ]
 */
function obtener_claves_foraneas($conexion, $tabla, $bd){
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

/**
 * Metadatos de columnas de una tabla.
 */
function obtener_meta_columnas($conexion, $tabla, $bd){
  $meta = [];
  $sql = "
    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT,
           COLUMN_KEY, EXTRA, CHARACTER_MAXIMUM_LENGTH, COLUMN_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = '".mysqli_real_escape_string($conexion,$bd)."'
      AND TABLE_NAME = '".mysqli_real_escape_string($conexion,$tabla)."'
  ";
  $resultado = mysqli_query($conexion, $sql);
  if($resultado){
    while($fila = mysqli_fetch_assoc($resultado)){
      $meta[$fila['COLUMN_NAME']] = $fila;
    }
  }
  return $meta;
}

/**
 * Tablas que referencian a una tabla dada (FK entrantes)
 */
function obtener_tablas_que_referencian($conexion, $tabla_referenciada, $bd){
  $refs = [];
  $sql = "
    SELECT TABLE_NAME, COLUMN_NAME
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = '".mysqli_real_escape_string($conexion,$bd)."'
      AND REFERENCED_TABLE_NAME = '".mysqli_real_escape_string($conexion,$tabla_referenciada)."'
  ";
  $resultado = mysqli_query($conexion, $sql);
  if($resultado){
    while($fila = mysqli_fetch_assoc($resultado)){
      $refs[] = [
        'tabla'   => $fila['TABLE_NAME'],
        'columna' => $fila['COLUMN_NAME']
      ];
    }
  }
  return $refs;
}

/**
 * Control de formulario adecuado para una columna NO FK.
 */
function render_input_para_columna($nombre_columna, $meta_columna, $valor_actual = ""){
  $data_type   = strtolower($meta_columna['DATA_TYPE']);
  $column_type = strtolower($meta_columna['COLUMN_TYPE']);
  $html = "";

  // Etiqueta
  $html .= "<label>".$nombre_columna."</label>";

  // tinyint(1) -> checkbox
  if($data_type === 'tinyint' && strpos($column_type, '(1)') !== false){
    $checked = ($valor_actual == 1 || $valor_actual === "1") ? "checked" : "";
    $html .= "<input type='checkbox' name='".$nombre_columna."' value='1' ".$checked.">";
    return $html;
  }

  switch($data_type){
    // Textos
    case 'varchar':
    case 'char':
    case 'tinytext':
    case 'text':
    case 'mediumtext':
    case 'longtext':
      $html .= "<input type='text' name='".$nombre_columna."' placeholder='".$nombre_columna."' value='".htmlspecialchars($valor_actual,ENT_QUOTES)."'>";
      break;

    // Números enteros
    case 'int':
    case 'integer':
    case 'tinyint':
    case 'smallint':
    case 'mediumint':
    case 'bigint':
    case 'year':
      $html .= "<input type='number' name='".$nombre_columna."' placeholder='".$nombre_columna."' value='".htmlspecialchars($valor_actual,ENT_QUOTES)."' step='1'>";
      break;

    // Números decimales
    case 'decimal':
    case 'numeric':
    case 'float':
    case 'double':
    case 'real':
      $html .= "<input type='number' name='".$nombre_columna."' placeholder='".$nombre_columna."' value='".htmlspecialchars($valor_actual,ENT_QUOTES)."' step='any'>";
      break;

    // Fechas
    case 'date':
      $html .= "<input type='date' name='".$nombre_columna."' value='".htmlspecialchars($valor_actual,ENT_QUOTES)."'>";
      break;

    case 'datetime':
    case 'timestamp':
      // datetime-local espera formato 'YYYY-MM-DDThh:mm'
      $valor = str_replace(" ", "T", $valor_actual);
      $html .= "<input type='datetime-local' name='".$nombre_columna."' value='".htmlspecialchars($valor,ENT_QUOTES)."'>";
      break;

    case 'time':
      $html .= "<input type='time' name='".$nombre_columna."' value='".htmlspecialchars($valor_actual,ENT_QUOTES)."'>";
      break;

    // ENUM y SET -> select
    case 'enum':
    case 'set':
      $html .= "<select name='".$nombre_columna."'>";
      $html .= "<option value=''>-- seleccionar --</option>";
      if(preg_match_all("/'([^']*)'/", $meta_columna['COLUMN_TYPE'], $matches)){
        foreach($matches[1] as $opcion){
          $selected = ($valor_actual == $opcion) ? "selected" : "";
          $html .= "<option value='".htmlspecialchars($opcion,ENT_QUOTES)."' ".$selected.">".$opcion."</option>";
        }
      }
      $html .= "</select>";
      break;

    // Otros tipos -> text genérico
    default:
      $html .= "<input type='text' name='".$nombre_columna."' placeholder='".$nombre_columna."' value='".htmlspecialchars($valor_actual,ENT_QUOTES)."'>";
      break;
  }

  return $html;
}

/**
 * Renderizar tabla HTML de resultados usando la misma lógica de FKs
 * que el listado principal (para los informes).
 */
function render_tabla_html_con_links($conexion, $tabla, $rows, $bd){
  if(!$rows || count($rows) === 0){
    echo "<p class='no-data'>Sin datos.</p>";
    return;
  }
  $foreignKeysLocal = obtener_claves_foraneas($conexion, $tabla, $bd);

  echo "<table class='report-table'>";
  // Cabecera
  $first = $rows[0];
  echo "<tr>";
  foreach($first as $k => $_){
    echo "<th>".$k."</th>";
  }
  echo "</tr>";

  // Filas
  foreach($rows as $fila){
    echo "<tr>";
    foreach($fila as $clave=>$valor){
      if(isset($foreignKeysLocal[$clave]) && $valor !== null && $valor !== ''){
        $fk = $foreignKeysLocal[$clave];
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
          echo "<td>".htmlspecialchars($texto_celda,ENT_QUOTES)."</td>";
        }else{
          echo "<td>".htmlspecialchars($valor,ENT_QUOTES)."</td>";
        }
      }else{
        echo "<td>".htmlspecialchars($valor,ENT_QUOTES)."</td>";
      }
    }
    echo "</tr>";
  }

  echo "</table>";
}
?>
<!doctype html>
<html lang="es">
  <head>
    <title>microERP</title>
    <meta charset="utf-8">
    <style>
      :root{
        --margen: 20px;
        --color_primario: indigo;
        --color_primario_suave: rgba(75,0,130,0.08);
        --color_secundario: aliceblue;
        --radio: 8px;
      }
      *{
        box-sizing:border-box;
      }
      html,body{
        width:100%;
        height:100%;
        padding:0;
        margin:0;
        font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
      }
      body{
        display:flex;
        background:linear-gradient(135deg, #f5f7ff 0%, #e8f0ff 50%, #fdfdff 100%);
        color:#222;
      }
      /* NAV LATERAL */
      nav{
        flex:1;
        min-width:240px;
        max-width:320px;
        padding:var(--margen);
        display:flex;
        flex-direction:column;
        gap:var(--margen);
        background:radial-gradient(circle at top left,#4b0082 0%,#2b004d 40%,#120024 100%);
        box-shadow:4px 0 20px rgba(0,0,0,0.25);
        color:white;
        position:relative;
        z-index:2;
      }
      #corporativo{
        display:flex;
        color:white;
        gap:calc(var(--margen)/2);
        align-items:center;
        justify-content:space-between;
        padding-bottom:var(--margen);
        border-bottom:1px solid rgba(255,255,255,0.15);
      }
      #corporativo img{
        width:56px;
        filter:drop-shadow(0 0 6px rgba(255,255,255,0.3));
      }
      #corporativo p{
        font-size:26px;
        margin:0;
        font-weight:700;
        letter-spacing:1px;
        text-shadow:0 0 6px rgba(0,0,0,0.3);
      }
      .logout{
        background:rgba(240,248,255,0.2);
        color:aliceblue;
        padding:6px 12px;
        border-radius:999px;
        text-decoration:none;
        font-size:12px;
        font-weight:600;
        border:1px solid rgba(240,248,255,0.4);
        transition:all 0.2s ease;
      }
      .logout:hover{
        background:aliceblue;
        color:var(--color_primario);
      }
      .login-user-label{
        font-size:11px;
        color:aliceblue;
        opacity:0.85;
        margin-right:6px;
      }

      nav>button{
        background:rgba(240,248,255,0.06);
        color:var(--color_secundario);
        padding:10px 12px;
        border-radius:var(--radio);
        border:1px solid transparent;
        display:flex;
        justify-content: space-between;
        align-items:center;
        cursor:pointer;
        transition:all 0.2s ease;
      }
      nav>button:hover{
        background:rgba(240,248,255,0.16);
        border-color:rgba(240,248,255,0.3);
        transform:translateX(2px);
      }
      .activo{
        background:rgba(240,248,255,0.25);
        border-color:rgba(240,248,255,0.7);
        transform:translateX(4px);
        box-shadow:0 0 10px rgba(240,248,255,0.4);
      }
      nav button a{
        text-decoration:none;
        color:inherit;
        font-size:13px;
        font-weight:600;
        text-transform:uppercase;
        letter-spacing:0.5px;
      }
      .anadir{
        width:22px;
        height:22px;
        background:aliceblue;
        color:var(--color_primario);
        border-radius:50%;
        line-height:22px;
        font-weight:bold;
        text-align:center;
        text-decoration:none;
        display:inline-block;
        box-shadow:0 0 6px rgba(0,0,0,0.3);
      }

      /* MAIN / DASHBOARD */
      main{
        flex:6;
        padding:var(--margen);
        overflow:auto;
        background:radial-gradient(circle at top,rgba(240,248,255,0.7) 0%,rgba(230,235,255,0.9) 40%,#f9fbff 100%);
        position:relative;
      }
      main::before{
        content:"";
        position:absolute;
        inset:0;
        background:radial-gradient(circle at bottom right,rgba(75,0,130,0.08) 0%,transparent 55%);
        pointer-events:none;
        z-index:-1;
      }
      h2{
        margin-top:0;
        margin-bottom:10px;
        color:var(--color_primario);
        text-shadow:0 0 4px rgba(255,255,255,0.8);
      }

      /* TABLAS */
      main table{
        width:100%;
        border:1px solid rgba(75,0,130,0.2);
        border-collapse:collapse;
        border-radius:var(--radio);
        overflow:hidden;
        background:white;
        box-shadow:0 4px 14px rgba(0,0,0,0.06);
      }
      main table tr:nth-child(even){
        background:#f9f9ff;
      }
      main table tr:hover{
        background:#eef2ff;
      }
      main table td{
        padding:10px 12px;
        vertical-align:top;
        font-size:13px;
      }
      main table th{
        background:linear-gradient(90deg,var(--color_primario),#7b3fb0);
        padding:10px 12px;
        color:aliceblue;
        text-align:left;
        font-size:12px;
        text-transform:uppercase;
        letter-spacing:0.7px;
      }

      .report-table{
        margin-bottom:var(--margen);
      }
      .no-data{
        font-size:13px;
        color:#666;
      }

      /* ACCIONES */
      .eliminar,
      .editar,
      .reportar{
        display:inline-flex;
        align-items:center;
        justify-content:center;
        width:24px;
        height:24px;
        border-radius:999px;
        text-decoration:none;
        color:white;
        margin-left:4px;
        font-size:12px;
        box-shadow:0 0 6px rgba(0,0,0,0.25);
        transition:transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
      }
      .eliminar{
        background:#c0392b;
      }
      .editar{
        background:#e67e22;
      }
      .reportar{
        background:#16a085;
      }
      .eliminar:hover,
      .editar:hover,
      .reportar:hover{
        transform:translateY(-1px) scale(1.03);
        box-shadow:0 0 10px rgba(0,0,0,0.35);
        opacity:0.95;
      }

      @keyframes aparece{
        0%{opacity:0;transform:translateX(-30px);}
        100%{opacity:1;transform:translateX(0px);}
      }

      /* FORMULARIOS */
      form{
        columns:2;
        gap:var(--margen);
        margin-top:10px;
      }
      form label{
        display:block;
        font-weight:600;
        margin-bottom:4px;
        font-size:12px;
        color:#444;
      }
      form input,
      form select{
        width:100%;
        padding:10px 12px;
        box-sizing:border-box;
        margin-bottom:var(--margen);
        border:1px solid rgba(75,0,130,0.3);
        border-radius:var(--radio);
        background:rgba(255,255,255,0.9);
        font-size:13px;
        transition:border 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
      }
      form input:focus,
      form select:focus{
        outline:none;
        border-color:var(--color_primario);
        box-shadow:0 0 0 2px rgba(75,0,130,0.15);
        background:white;
      }
      form input[type=checkbox]{
        width:auto;
        padding:0;
        margin-top:5px;
        box-shadow:none;
      }
      form input[type=submit]{
        background:linear-gradient(90deg,var(--color_primario),#7b3fb0);
        color:white;
        cursor:pointer;
        border:none;
        font-weight:600;
        text-transform:uppercase;
        letter-spacing:0.8px;
        box-shadow:0 4px 10px rgba(75,0,130,0.4);
      }
      form input[type=submit]:hover{
        box-shadow:0 5px 14px rgba(75,0,130,0.6);
        transform:translateY(-1px);
      }

      /* LOGIN */
      .login-box{
        max-width:420px;
        margin:80px auto;
        background:white;
        padding:var(--margen);
        border-radius:16px;
        border:1px solid rgba(75,0,130,0.2);
        box-shadow:0 14px 40px rgba(0,0,0,0.18);
        column-count:1;
        position:relative;
        overflow:hidden;
      }
      .login-box::before{
        content:"";
        position:absolute;
        inset:0;
        background:radial-gradient(circle at top,#eef0ff 0%,transparent 55%);
        opacity:0.9;
        pointer-events:none;
      }
      .login-box h2{
        margin-top:0;
        margin-bottom:var(--margen);
        color:var(--color_primario);
        position:relative;
        z-index:1;
      }
      .login-box form{
        columns:1;
        position:relative;
        z-index:1;
      }
      .login-error{
        background:#ffdddd;
        border:1px solid #cc0000;
        color:#660000;
        padding:10px;
        border-radius:var(--radio);
        margin-bottom:var(--margen);
        font-size:14px;
        position:relative;
        z-index:1;
      }

      /* DASHBOARD / CHARTS */
      .dashboard-intro{
        margin-bottom:var(--margen);
        font-size:14px;
        color:#555;
        max-width:700px;
      }
      .charts-grid{
        display:grid;
        grid-template-columns:repeat(auto-fit,minmax(260px,1fr));
        gap:var(--margen);
      }
      .chart{
        background:white;
        border-radius:var(--radio);
        border:1px solid rgba(75,0,130,0.18);
        padding:var(--margen);
        box-sizing:border-box;
        box-shadow:0 6px 18px rgba(0,0,0,0.08);
        position:relative;
        overflow:hidden;
      }
      .chart::before{
        content:"";
        position:absolute;
        inset:0;
        background:radial-gradient(circle at top right,rgba(75,0,130,0.08) 0%,transparent 60%);
        pointer-events:none;
      }
      .chart h3{
        margin-top:0;
        margin-bottom:10px;
        font-size:15px;
        color:var(--color_primario);
        position:relative;
        z-index:1;
      }
      .chart-subtitle{
        font-size:11px;
        color:#777;
        margin-bottom:8px;
        position:relative;
        z-index:1;
      }
      .chart-bars{
        display:flex;
        flex-direction:column;
        gap:6px;
        position:relative;
        z-index:1;
      }
      .chart-bar{
        position:relative;
        height:24px;
        background:var(--color_primario_suave);
        border-radius:12px;
        overflow:hidden;
      }
      .chart-fill{
        height:100%;
        background:linear-gradient(90deg,var(--color_primario),#7b3fb0);
        opacity:0.85;
      }
      .chart-label{
        position:absolute;
        left:10px;
        top:4px;
        font-size:11px;
        color:white;
        text-shadow:0 0 3px rgba(0,0,0,0.4);
        white-space:nowrap;
        overflow:hidden;
        text-overflow:ellipsis;
        right:6px;
      }

      .back-link{
        margin-bottom:var(--margen);
        display:inline-block;
        text-decoration:none;
        color:var(--color_primario);
        font-size:13px;
        padding:4px 8px;
        border-radius:999px;
        background:rgba(75,0,130,0.07);
      }
      .back-link::before{
        content:"← ";
      }
      .subsection{
        margin-top:var(--margen);
      }
      .subsection h3{
        margin-bottom:6px;
        color:#333;
      }
      .subsection h4{
        margin:8px 0 4px;
        font-size:13px;
        color:#555;
      }

      @media (max-width:900px){
        body{flex-direction:column;}
        nav{
          flex:none;
          max-width:none;
          box-shadow:0 4px 12px rgba(0,0,0,0.2);
        }
      }
    </style>
  </head>
  <body>
    <nav>
      <div id="corporativo">
        <div style="display:flex;align-items:center;gap:calc(var(--margen)/2);">
          <img src="https://jocarsa.github.io/logos/logos/jocarsa%20%7C%20AliceBlue.svg" alt="jocarsa">
          <p>jocarsa</p>
        </div>
        <?php if($logged_in): ?>
          <div>
            <span class="login-user-label"><?php echo htmlspecialchars($_SESSION['usuario']); ?></span>
            <a href="?logout=1" class="logout">Salir</a>
          </div>
        <?php endif; ?>
      </div>

      <?php
        // Listado de tablas SOLO si está logueado
        if ($logged_in && isset($conexion) && $conexion){
          $resultado = mysqli_query($conexion, "SHOW TABLES;");
          $tabla_actual = isset($_GET['tabla']) ? $_GET['tabla'] : "";
          while($fila = mysqli_fetch_assoc($resultado)){
            $nombre_tabla = array_values($fila)[0];
            $clase = ($nombre_tabla == $tabla_actual) ? "activo" : "";
            echo "<button class='".$clase."'>";
              echo "<a href='?tabla=".$nombre_tabla."'>".$nombre_tabla."</a>";
              if($nombre_tabla == $tabla_actual){
                echo "<a href='?operacion=añadir&tabla=".$tabla_actual."' class='anadir'>+</a>";
              }
            echo "</button>";
          }
        }
      ?>
    </nav>
    <main>
      <?php
        // Si NO está logueado -> login
        if(!$logged_in){
          echo "<div class='login-box'>";
          echo "<h2>Acceso a microERP</h2>";
          if($login_error){
            echo "<div class='login-error'>".$login_error."</div>";
          }
          echo "<form method='POST' action=''>";
          echo "<input type='hidden' name='accion' value='login'>";
          echo "<input type='text' name='usuario' placeholder='Usuario' autofocus>";
          echo "<input type='password' name='contrasena' placeholder='Contraseña'>";
          echo "<input type='submit' value='Entrar'>";
          echo "</form>";
          echo "<p style='font-size:12px;color:#555;margin-top:10px;'>Usuario inicial: <b>jocarsa</b> · Contraseña: <b>jocarsa</b></p>";
          echo "</div>";
        } else {
          // Lógica del microERP
          if(isset($_GET['tabla'])){
            $tabla      = $_GET['tabla'];
            $operacion  = $_GET['operacion'] ?? '';
            $id         = isset($_GET['id']) ? intval($_GET['id']) : null;

            $foreignKeys  = obtener_claves_foraneas($conexion, $tabla, $db_name);
            $columnMeta   = obtener_meta_columnas($conexion, $tabla, $db_name);

            // Eliminación
            if($operacion === "eliminar" && $id !== null){
              mysqli_query(
                $conexion,
                "DELETE FROM ".$tabla." WHERE Identificador = ".$id.";"
              );
              $operacion = '';
            }

            // AÑADIR
            if($operacion === "añadir"){
              // Procesar inserción si viene por POST
              if($_SERVER['REQUEST_METHOD'] === 'POST' && (!isset($_POST['accion']) || $_POST['accion'] !== 'login')){
                $columnas = [];
                $valores  = [];

                foreach($columnMeta as $nombre_columna => $meta_columna){
                  if($nombre_columna == 'Identificador'){ continue; }

                  $data_type   = strtolower($meta_columna['DATA_TYPE']);
                  $column_type = strtolower($meta_columna['COLUMN_TYPE']);

                  // tinyint(1) checkbox
                  if($data_type === 'tinyint' && strpos($column_type,'(1)') !== false){
                    $valor = isset($_POST[$nombre_columna]) ? 1 : 0;
                    $columnas[] = "`".$nombre_columna."`";
                    $valores[]  = intval($valor);
                    continue;
                  }

                  if(isset($_POST[$nombre_columna]) && $_POST[$nombre_columna] !== ''){
                    $columnas[] = "`".$nombre_columna."`";
                    $valores[]  = "'".mysqli_real_escape_string($conexion,$_POST[$nombre_columna])."'";
                  }
                }

                if(count($columnas) > 0){
                  $sql_insert = "INSERT INTO ".$tabla." (".implode(",",$columnas).") VALUES (".implode(",",$valores).")";
                  mysqli_query($conexion, $sql_insert);
                }
              }

              // Formulario de alta
              echo "<a href='?tabla=".$tabla."' class='back-link'>Volver al listado</a>";
              echo "<h2>Añadir registro en ".$tabla."</h2>";
              echo "<form action='?operacion=añadir&tabla=".$tabla."' method='POST'>";

              foreach($columnMeta as $nombre_columna => $meta_columna){
                if($nombre_columna == 'Identificador'){ continue; }

                // FK: select
                if(isset($foreignKeys[$nombre_columna])){
                  $fk = $foreignKeys[$nombre_columna];
                  $tabla_fk   = $fk['tabla'];
                  $columna_fk = $fk['columna'];

                  echo "<label>".$nombre_columna."</label>";
                  echo "<select name='".$nombre_columna."'>";
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
                  echo render_input_para_columna($nombre_columna, $meta_columna);
                }
              }

              echo "<input type='submit' value='Guardar'>";
              echo "</form>";

            // EDITAR
            } elseif($operacion === "editar" && $id !== null){

              // Cargamos la fila actual
              $res_actual = mysqli_query($conexion, "SELECT * FROM ".$tabla." WHERE Identificador = ".$id." LIMIT 1;");
              $fila_actual = $res_actual ? mysqli_fetch_assoc($res_actual) : null;

              if(!$fila_actual){
                echo "<a href='?tabla=".$tabla."' class='back-link'>Volver al listado</a>";
                echo "<p>No se ha encontrado el registro a editar.</p>";
              } else {
                // Procesar actualización
                if($_SERVER['REQUEST_METHOD'] === 'POST' && (!isset($_POST['accion']) || $_POST['accion'] !== 'login')){
                  $sets = [];

                  foreach($columnMeta as $nombre_columna => $meta_columna){
                    if($nombre_columna == 'Identificador'){ continue; }

                    $data_type   = strtolower($meta_columna['DATA_TYPE']);
                    $column_type = strtolower($meta_columna['COLUMN_TYPE']);

                    // tinyint(1) checkbox
                    if($data_type === 'tinyint' && strpos($column_type,'(1)') !== false){
                      $valor = isset($_POST[$nombre_columna]) ? 1 : 0;
                      $sets[] = "`".$nombre_columna."`=".intval($valor);
                      continue;
                    }

                    if(isset($_POST[$nombre_columna])){
                      $valor = $_POST[$nombre_columna];
                      $sets[] = "`".$nombre_columna."` = '".mysqli_real_escape_string($conexion,$valor)."'";
                    }
                  }

                  if(count($sets) > 0){
                    $sql_update = "UPDATE ".$tabla." SET ".implode(", ",$sets)." WHERE Identificador = ".$id;
                    mysqli_query($conexion, $sql_update);
                  }

                  // Recargar fila actualizada
                  $res_actual = mysqli_query($conexion, "SELECT * FROM ".$tabla." WHERE Identificador = ".$id." LIMIT 1;");
                  $fila_actual = $res_actual ? mysqli_fetch_assoc($res_actual) : $fila_actual;
                }

                echo "<a href='?tabla=".$tabla."' class='back-link'>Volver al listado</a>";
                echo "<h2>Editar registro en ".$tabla." (ID ".$id.")</h2>";
                echo "<form action='?operacion=editar&tabla=".$tabla."&id=".$id."' method='POST'>";

                // Identificador como solo lectura
                if(isset($fila_actual['Identificador'])){
                  echo "<label>Identificador</label>";
                  echo "<input type='text' value='".htmlspecialchars($fila_actual['Identificador'],ENT_QUOTES)."' disabled>";
                }

                foreach($columnMeta as $nombre_columna => $meta_columna){
                  if($nombre_columna == 'Identificador'){ continue; }
                  $valor_actual = $fila_actual[$nombre_columna] ?? "";

                  if(isset($foreignKeys[$nombre_columna])){
                    $fk = $foreignKeys[$nombre_columna];
                    $tabla_fk   = $fk['tabla'];
                    $columna_fk = $fk['columna'];

                    echo "<label>".$nombre_columna."</label>";
                    echo "<select name='".$nombre_columna."'>";
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
                        $selected = ($valor_actual == $value_opcion) ? "selected" : "";
                        echo "<option value='".$value_opcion."' ".$selected.">".$texto_opcion."</option>";
                      }
                    }

                    echo "</select>";
                  }else{
                    echo render_input_para_columna($nombre_columna, $meta_columna, $valor_actual);
                  }
                }

                echo "<input type='submit' value='Guardar cambios'>";
                echo "</form>";
              }

            // INFORME
            } elseif($operacion === "report" && $id !== null){

              echo "<a href='?tabla=".$tabla."' class='back-link'>Volver al listado</a>";

              // Fila actual
              $res_actual = mysqli_query($conexion, "SELECT * FROM ".$tabla." WHERE Identificador = ".$id." LIMIT 1;");
              $fila_actual = $res_actual ? mysqli_fetch_assoc($res_actual) : null;

              if(!$fila_actual){
                echo "<p>No se ha encontrado el registro solicitado.</p>";
              } else {
                echo "<h2>Informe de ".$tabla." (ID ".$id.")</h2>";

                // Registro principal (con misma lógica de FKs)
                echo "<div class='subsection'>";
                echo "<h3>Registro principal</h3>";
                render_tabla_html_con_links($conexion, $tabla, [$fila_actual], $db_name);
                echo "</div>";

                // Datos que este registro referencia (FK salientes)
                echo "<div class='subsection'>";
                echo "<h3>Datos referenciados por este registro</h3>";

                $hay_referenciados = false;
                foreach($foreignKeys as $columna_fk_local => $info_fk){
                  $valor_fk = $fila_actual[$columna_fk_local] ?? null;
                  if($valor_fk === null || $valor_fk === ''){ continue; }

                  $tabla_fk   = $info_fk['tabla'];
                  $col_fk     = $info_fk['columna'];

                  $sql_fk = "SELECT * FROM ".$tabla_fk." WHERE ".$col_fk." = '".mysqli_real_escape_string($conexion,$valor_fk)."'";
                  $res_fk = mysqli_query($conexion, $sql_fk);
                  if($res_fk && mysqli_num_rows($res_fk) > 0){
                    $hay_referenciados = true;
                    $rows_fk = [];
                    while($row_fk = mysqli_fetch_assoc($res_fk)){
                      $rows_fk[] = $row_fk;
                    }

                    echo "<h4>".$tabla_fk." (por ".$columna_fk_local.")</h4>";
                    render_tabla_html_con_links($conexion, $tabla_fk, $rows_fk, $db_name);
                  }
                }
                if(!$hay_referenciados){
                  echo "<p class='no-data'>No hay referencias salientes.</p>";
                }
                echo "</div>";

                // Tablas que referencian a este registro (FK entrantes)
                echo "<div class='subsection'>";
                echo "<h3>Datos relacionados que apuntan a este registro</h3>";

                $refs_entrantes = obtener_tablas_que_referencian($conexion, $tabla, $db_name);
                if(count($refs_entrantes) === 0){
                  echo "<p class='no-data'>No hay tablas que referencien a esta entidad.</p>";
                } else {
                  $hay_entrantes = false;
                  foreach($refs_entrantes as $ref){
                    $tabla_hija   = $ref['tabla'];
                    $columna_hija = $ref['columna'];

                    $sql_hija = "SELECT * FROM ".$tabla_hija." WHERE ".$columna_hija." = ".$id;
                    $res_hija = mysqli_query($conexion, $sql_hija);
                    if($res_hija && mysqli_num_rows($res_hija) > 0){
                      $hay_entrantes = true;
                      $rows_hija = [];
                      while($fila_hija = mysqli_fetch_assoc($res_hija)){
                        $rows_hija[] = $fila_hija;
                      }

                      echo "<h4>".$tabla_hija." (columna ".$columna_hija.")</h4>";
                      render_tabla_html_con_links($conexion, $tabla_hija, $rows_hija, $db_name);
                    }
                  }
                  if(!$hay_entrantes){
                    echo "<p class='no-data'>No hay registros entrantes que apunten a este ID.</p>";
                  }
                }

                echo "</div>";
              }

            // LISTADO
            } else {
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
                    echo "<th>Acciones</th>";
                  echo "</tr>";
                }

                echo "<tr>";
                foreach($fila as $clave=>$valor){
                  // Si es FK, mostramos fila referenciada
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
                      echo "<td>".htmlspecialchars($texto_celda,ENT_QUOTES)."</td>";
                    }else{
                      echo "<td>".htmlspecialchars($valor,ENT_QUOTES)."</td>";
                    }
                  }else{
                    echo "<td>".htmlspecialchars($valor,ENT_QUOTES)."</td>";
                  }
                }

                // Acciones: editar, informe, eliminar
                $id_fila = isset($fila['Identificador']) ? intval($fila['Identificador']) : 0;
                echo "<td>";
                echo "<a href='?operacion=editar&tabla=".$tabla."&id=".$id_fila."' class='editar'>✏</a>";
                echo "<a href='?operacion=report&tabla=".$tabla."&id=".$id_fila."' class='reportar'>i</a>";
                echo "<a href='?operacion=eliminar&tabla=".$tabla."&id=".$id_fila."' class='eliminar'>×</a>";
                echo "</td>";

                echo "</tr>";

                $contador++;
              }
              echo "</table>";
            }
          } else {
            // DASHBOARD INICIAL: gráficos de campos ENUM/SET y FKs
            echo "<h2>Dashboard de microERP</h2>";
            echo "<p class='dashboard-intro'>
              Resumen gráfico de la información categórica y relacional del sistema:
              campos <b>ENUM/SET</b> y campos de <b>clave foránea</b> en todas las tablas.
            </p>";

            $resultado = mysqli_query($conexion, "SHOW TABLES;");
            echo "<div class='charts-grid'>";
            while($fila = mysqli_fetch_assoc($resultado)){
              $tabla = array_values($fila)[0];
              $meta  = obtener_meta_columnas($conexion, $tabla, $db_name);
              $fksTabla = obtener_claves_foraneas($conexion, $tabla, $db_name);

              // 1) Campos ENUM/SET
              foreach($meta as $nombre_columna => $meta_columna){
                $data_type = strtolower($meta_columna['DATA_TYPE']);
                if($data_type !== 'enum' && $data_type !== 'set'){ continue; }

                $sql_dist = "
                  SELECT ".$nombre_columna." AS valor, COUNT(*) AS total
                  FROM ".$tabla."
                  GROUP BY ".$nombre_columna."
                  ORDER BY total DESC
                ";
                $res_dist = mysqli_query($conexion, $sql_dist);
                if(!$res_dist || mysqli_num_rows($res_dist) < 1){ continue; }

                $valores = [];
                $max = 0;
                while($fila_dist = mysqli_fetch_assoc($res_dist)){
                  $v = $fila_dist['valor'];
                  $c = (int)$fila_dist['total'];
                  $valores[] = [
                    'label' => ($v === null || $v === '' ? '(vacío)' : $v),
                    'total' => $c
                  ];
                  if($c > $max){ $max = $c; }
                }
                if($max == 0){ continue; }

                echo "<div class='chart'>";
                echo "<h3>".$tabla." · ".$nombre_columna."</h3>";
                echo "<div class='chart-subtitle'>Distribución de valores ENUM/SET</div>";
                echo "<div class='chart-bars'>";
                foreach($valores as $dato){
                  $label = $dato['label'];
                  $c     = $dato['total'];
                  $width = round(($c / $max) * 100, 2);
                  $text  = htmlspecialchars($label,ENT_QUOTES)." (".$c.")";
                  echo "<div class='chart-bar'>";
                  echo "<div class='chart-fill' style='width:".$width."%;'></div>";
                  echo "<div class='chart-label'>".$text."</div>";
                  echo "</div>";
                }
                echo "</div>";
                echo "</div>";
              }

              // 2) Campos FK: distribución por valor referenciado
              foreach($fksTabla as $columna_fk => $info_fk){
                $tabla_ref = $info_fk['tabla'];
                $col_ref   = $info_fk['columna'];

                $sql_dist_fk = "
                  SELECT ".$columna_fk." AS valor, COUNT(*) AS total
                  FROM ".$tabla."
                  GROUP BY ".$columna_fk."
                  ORDER BY total DESC
                ";
                $res_dist_fk = mysqli_query($conexion, $sql_dist_fk);
                if(!$res_dist_fk || mysqli_num_rows($res_dist_fk) < 1){ continue; }

                $valores_fk = [];
                $max_fk = 0;

                while($fila_dist = mysqli_fetch_assoc($res_dist_fk)){
                  $valor_fk = $fila_dist['valor'];
                  $c        = (int)$fila_dist['total'];

                  if($valor_fk === null || $valor_fk === ''){
                    $label = '(sin valor)';
                  }else{
                    // Miramos fila referenciada para label
                    $sql_ref = "
                      SELECT *
                      FROM ".$tabla_ref."
                      WHERE ".$col_ref." = '".mysqli_real_escape_string($conexion,$valor_fk)."'
                      LIMIT 1
                    ";
                    $res_ref = mysqli_query($conexion, $sql_ref);
                    if($res_ref && $fila_ref = mysqli_fetch_assoc($res_ref)){
                      $partes = [];
                      foreach($fila_ref as $k2=>$v2){
                        $partes[] = $v2;
                      }
                      $label = implode(" | ", $partes);
                    }else{
                      $label = 'ID '.$valor_fk.' (huérfano)';
                    }
                  }

                  $valores_fk[] = [
                    'label' => $label,
                    'total' => $c
                  ];
                  if($c > $max_fk){ $max_fk = $c; }
                }

                if($max_fk == 0){ continue; }

                echo "<div class='chart'>";
                echo "<h3>".$tabla." · ".$columna_fk."</h3>";
                echo "<div class='chart-subtitle'>Distribución por referencia a ".$tabla_ref."</div>";
                echo "<div class='chart-bars'>";
                foreach($valores_fk as $dato){
                  $label = $dato['label'];
                  $c     = $dato['total'];
                  $width = round(($c / $max_fk) * 100, 2);
                  $text  = htmlspecialchars($label,ENT_QUOTES)." (".$c.")";
                  echo "<div class='chart-bar'>";
                  echo "<div class='chart-fill' style='width:".$width."%;'></div>";
                  echo "<div class='chart-label'>".$text."</div>";
                  echo "</div>";
                }
                echo "</div>";
                echo "</div>";
              }
            }
            echo "</div>";
          }
        }
      ?>
    </main>
  </body>
</html>

