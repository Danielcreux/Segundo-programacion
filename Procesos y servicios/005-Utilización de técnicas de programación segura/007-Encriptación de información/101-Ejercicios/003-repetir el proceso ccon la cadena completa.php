<?php
  $cadena = "Jose Vicente";
  $resultado = "";
  for($i = 0;$i<strlen($cadena);$i++){
    $ascii = ord($cadena[$i]);
    $ascii += 5;
    $resultado .= chr($ascii);
  }
  echo $resultado;
  
  $desencriptado = "";
  for($i = 0;$i<strlen($resultado);$i++){
    $ascii = ord($resultado[$i]);
    $ascii -= 5;
    $desencriptado .= chr($ascii);
  }
  echo $desencriptado;
?>
