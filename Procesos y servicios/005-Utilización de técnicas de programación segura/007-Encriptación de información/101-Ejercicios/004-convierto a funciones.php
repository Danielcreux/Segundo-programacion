<?php
  $cadena = "Jose Vicente";
  
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
  
  echo $cadena."<br>";
  $encriptado = encripta($cadena);
  echo $encriptado."<br>";
  $desencriptado = desencripta($encriptado);
  echo $desencriptado."<br>";
?>








