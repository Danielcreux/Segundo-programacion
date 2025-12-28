<?php
  $cadena = "Jose Vicente";
  class Encriptador{
    function encripta($objeto){
      $resultado = "";
      for($i = 0;$i<strlen($objeto);$i++){
        $ascii = ord($objeto[$i]);
        $ascii += 5;
        $resultado .= chr($ascii);
      }
      return $resultado;
    }
    function desencripta($objeto){
      $desencriptado = "";
      for($i = 0;$i<strlen($objeto);$i++){
        $ascii = ord($objeto[$i]);
        $ascii -= 5;
        $desencriptado .= chr($ascii);
      }
      return $desencriptado;
    }
  }
  <?php
// Conexión a la base de datos
$mysqli = new mysqli("localhost", "tienda2526", "tienda2526", "tienda2526");

$sql = "SELECT * FROM clientes";
$result = $mysqli->query($sql);

$datos = [];

while ($row = $result->fetch_assoc()) {
    $datos[] = $row;
}

// Imprimir como JSON
header('Content-Type: application/json; charset=utf-8');
echo json_encode($datos, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);


?>








