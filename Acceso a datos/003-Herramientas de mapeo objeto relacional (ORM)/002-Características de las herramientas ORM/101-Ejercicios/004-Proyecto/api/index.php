<?php
/*
   Enrutador de muestra
   Sistemas de gestión empresarial
   Alimenta a la interfaz, bebe de la base de datos
*/
include "../lib/JVDB.php";

// Ejemplo de uso
$conexion = new JVDB("localhost", "blog2526", "blog2526", "blog2526");

$routes = [
    'GET' => [
        '/' => function() {
            echo "Home Page";
        },
        '/contact' => function() {
            echo "Contact Page";
        },
        '/menu' => function() use ($conexion) {
            echo $conexion->tablas();
        },
        '/tabla' => function() use ($conexion) {
            echo $conexion->seleccionar("entradas");
        },
    ]
];

$method = $_SERVER['REQUEST_METHOD'];

// Obtengo solo la ruta, sin query string
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// Normalizo codificación (espacios, acentos, etc.)
$path = urldecode($path);

// Directorio base donde está este script (api)
$base = rtrim(dirname($_SERVER['SCRIPT_NAME']), '/');

// Quito el base de delante
$finalPath = substr($path, strlen($base));

if ($finalPath === '' || $finalPath === false) {
    $finalPath = '/';
}

// DEBUG opcional:
// var_dump($path, $base, $finalPath);

if (isset($routes[$method][$finalPath])) {
    $routes[$method][$finalPath]();
} else {
    print_r(array_keys($routes['GET']));
    echo "<h2>404 - Route not found</h2>";
}
