<?php
// MODO DEBUG (actívalo mientras pruebas)
error_reporting(E_ALL);
ini_set('display_errors', 1);

$cadena = "Jose Vicente";

class Encriptador {
    function encripta($objeto){
        $resultado = "";
        for($i = 0; $i < strlen($objeto); $i++){
            $ascii = ord($objeto[$i]);
            $ascii += 5;
            $resultado .= chr($ascii);
        }
        return $resultado;
    }
    function desencripta($objeto){
        $desencriptado = "";
        for($i = 0; $i < strlen($objeto); $i++){
            $ascii = ord($objeto[$i]);
            $ascii -= 5;
            $desencriptado .= chr($ascii);
        }
        return $desencriptado;
    }
}

$enc = new Encriptador();

// Conexión a la base de datos
$mysqli = new mysqli("localhost", "tienda2526", "tienda2526", "tienda2526");

// Comprobar conexión
if ($mysqli->connect_errno) {
    die("Error de conexión: " . $mysqli->connect_error);
}

$sql = "SELECT * FROM clientes";
$result = $mysqli->query($sql);

// Comprobar consulta
if (!$result) {
    die("Error en la consulta: " . $mysqli->error);
}

$datos = [];

while ($row = $result->fetch_assoc()) {
    $filaEncriptada = [];
    foreach ($row as $campo => $valor) {
        $valor = (string)$valor;

        // 1) Cifro con tu algoritmo
        $cifradoBinario = $enc->encripta($valor);
        // 2) Lo convierto a texto seguro para JSON
        $filaEncriptada[$campo] = base64_encode($cifradoBinario);
    }
    $datos[] = $filaEncriptada;
}

// Imprimir como JSON
header('Content-Type: application/json; charset=utf-8');

$json = json_encode($datos, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);

// Comprobar errores de json_encode por si acaso
if ($json === false) {
    die("Error al codificar JSON: " . json_last_error_msg());
}

echo $json;

