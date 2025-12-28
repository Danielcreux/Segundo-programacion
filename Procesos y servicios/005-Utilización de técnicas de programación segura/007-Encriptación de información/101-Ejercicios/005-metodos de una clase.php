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
  $encriptador = new Encriptador();
  echo $cadena."<br>";
  $encriptado = $encriptador->encripta($cadena);
  echo $encriptado."<br>";
  $desencriptado = $encriptador->desencripta($encriptado);
  echo $desencriptado."<br>";
?>








