<?php
/*
   Enrutador de muestra
   Sistemas de gestión empresarial
   Alimenta a la interfaz, bebe de la base de datos
*/

$routes = [
    'GET' => [
        '/' => function() { echo "Home Page"; },
        '/contact' => function() { echo "Contact Page"; },
        '/menu' => function() { 
            $elementos = ['Productos','Servicios','Empleados'];
            echo json_encode($elementos, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
          },
        '/tabla' => function() { 

            $alumnos = [
                [
                    "id" => 1,
                    "nombre" => "Ana",
                    "apellidos" => "García López",
                    "curso" => "DAM 1",
                    "nota" => 8.5,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 2,
                    "nombre" => "Luis",
                    "apellidos" => "Martínez Pérez",
                    "curso" => "DAW 2",
                    "nota" => 6.7,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 3,
                    "nombre" => "María",
                    "apellidos" => "Sánchez Ruiz",
                    "curso" => "ASIR 1",
                    "nota" => 4.9,
                    "estado" => "Suspenso"
                ],
                [
                    "id" => 4,
                    "nombre" => "Carlos",
                    "apellidos" => "Fernández Gil",
                    "curso" => "DAM 2",
                    "nota" => 9.1,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 5,
                    "nombre" => "Elena",
                    "apellidos" => "Hernández Soto",
                    "curso" => "DAW 1",
                    "nota" => 7.3,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 6,
                    "nombre" => "Javier",
                    "apellidos" => "Romero Ortiz",
                    "curso" => "ASIR 2",
                    "nota" => 5.0,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 7,
                    "nombre" => "Laura",
                    "apellidos" => "Navas Peña",
                    "curso" => "DAM 1",
                    "nota" => 3.8,
                    "estado" => "Suspenso"
                ],
                [
                    "id" => 8,
                    "nombre" => "Sergio",
                    "apellidos" => "Molina Torres",
                    "curso" => "DAW 2",
                    "nota" => 9.4,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 9,
                    "nombre" => "Patricia",
                    "apellidos" => "Ibáñez Campos",
                    "curso" => "ASIR 1",
                    "nota" => 6.1,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 10,
                    "nombre" => "Pablo",
                    "apellidos" => "Vidal Rubio",
                    "curso" => "DAM 2",
                    "nota" => 4.2,
                    "estado" => "Suspenso"
                ],
                [
                    "id" => 11,
                    "nombre" => "Daniel",
                    "apellidos" => "Santos Muñoz",
                    "curso" => "DAW 1",
                    "nota" => 7.9,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 12,
                    "nombre" => "Irene",
                    "apellidos" => "López Cordero",
                    "curso" => "ASIR 2",
                    "nota" => 8.2,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 13,
                    "nombre" => "Raúl",
                    "apellidos" => "Castro Herrero",
                    "curso" => "DAM 1",
                    "nota" => 2.7,
                    "estado" => "Suspenso"
                ],
                [
                    "id" => 14,
                    "nombre" => "Cristina",
                    "apellidos" => "Requena Bravo",
                    "curso" => "DAW 2",
                    "nota" => 5.5,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 15,
                    "nombre" => "Alberto",
                    "apellidos" => "Morales Sanz",
                    "curso" => "ASIR 1",
                    "nota" => 6.9,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 16,
                    "nombre" => "Lucía",
                    "apellidos" => "Jiménez Gallego",
                    "curso" => "DAM 2",
                    "nota" => 9.8,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 17,
                    "nombre" => "Álvaro",
                    "apellidos" => "Rivas Lozano",
                    "curso" => "DAW 1",
                    "nota" => 4.6,
                    "estado" => "Suspenso"
                ],
                [
                    "id" => 18,
                    "nombre" => "Noelia",
                    "apellidos" => "Benítez Roldán",
                    "curso" => "ASIR 2",
                    "nota" => 7.1,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 19,
                    "nombre" => "Rubén",
                    "apellidos" => "Marín León",
                    "curso" => "DAM 1",
                    "nota" => 5.9,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 20,
                    "nombre" => "Sara",
                    "apellidos" => "Pascual Arias",
                    "curso" => "DAW 2",
                    "nota" => 3.5,
                    "estado" => "Suspenso"
                ],
                [
                    "id" => 21,
                    "nombre" => "Hugo",
                    "apellidos" => "Suárez Crespo",
                    "curso" => "ASIR 1",
                    "nota" => 8.0,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 22,
                    "nombre" => "Alba",
                    "apellidos" => "Domínguez Vega",
                    "curso" => "DAM 2",
                    "nota" => 7.7,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 23,
                    "nombre" => "Mario",
                    "apellidos" => "Serrano Lozano",
                    "curso" => "DAW 1",
                    "nota" => 2.9,
                    "estado" => "Suspenso"
                ],
                [
                    "id" => 24,
                    "nombre" => "Nuria",
                    "apellidos" => "Calvo Riera",
                    "curso" => "ASIR 2",
                    "nota" => 6.4,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 25,
                    "nombre" => "Jorge",
                    "apellidos" => "Vega Carrasco",
                    "curso" => "DAM 1",
                    "nota" => 9.0,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 26,
                    "nombre" => "Paula",
                    "apellidos" => "Silva Costa",
                    "curso" => "DAW 2",
                    "nota" => 5.2,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 27,
                    "nombre" => "Óscar",
                    "apellidos" => "Navarro Castaño",
                    "curso" => "ASIR 1",
                    "nota" => 4.0,
                    "estado" => "Suspenso"
                ],
                [
                    "id" => 28,
                    "nombre" => "Beatriz",
                    "apellidos" => "Herrera Pardo",
                    "curso" => "DAM 2",
                    "nota" => 7.0,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 29,
                    "nombre" => "Víctor",
                    "apellidos" => "Prieto Dávila",
                    "curso" => "DAW 1",
                    "nota" => 6.3,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 30,
                    "nombre" => "Rocío",
                    "apellidos" => "Aguilar Pino",
                    "curso" => "ASIR 2",
                    "nota" => 3.3,
                    "estado" => "Suspenso"
                ],
                [
                    "id" => 31,
                    "nombre" => "Gonzalo",
                    "apellidos" => "Campos Valdés",
                    "curso" => "DAM 1",
                    "nota" => 8.9,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 32,
                    "nombre" => "Marta",
                    "apellidos" => "Soler Martí",
                    "curso" => "DAW 2",
                    "nota" => 7.6,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 33,
                    "nombre" => "Adrián",
                    "apellidos" => "Pérez Lafuente",
                    "curso" => "ASIR 1",
                    "nota" => 5.8,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 34,
                    "nombre" => "Natalia",
                    "apellidos" => "Varela Rico",
                    "curso" => "DAM 2",
                    "nota" => 4.4,
                    "estado" => "Suspenso"
                ],
                [
                    "id" => 35,
                    "nombre" => "Diego",
                    "apellidos" => "Soto Rivas",
                    "curso" => "DAW 1",
                    "nota" => 8.1,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 36,
                    "nombre" => "Claudia",
                    "apellidos" => "Rey Serrat",
                    "curso" => "ASIR 2",
                    "nota" => 6.0,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 37,
                    "nombre" => "Iván",
                    "apellidos" => "Muñoz Rueda",
                    "curso" => "DAM 1",
                    "nota" => 2.5,
                    "estado" => "Suspenso"
                ],
                [
                    "id" => 38,
                    "nombre" => "Silvia",
                    "apellidos" => "Carrasco Roca",
                    "curso" => "DAW 2",
                    "nota" => 9.3,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 39,
                    "nombre" => "Tomás",
                    "apellidos" => "Durán Lillo",
                    "curso" => "ASIR 1",
                    "nota" => 7.4,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 40,
                    "nombre" => "Alicia",
                    "apellidos" => "Campos Naranjo",
                    "curso" => "DAM 2",
                    "nota" => 3.9,
                    "estado" => "Suspenso"
                ],
                [
                    "id" => 41,
                    "nombre" => "Felipe",
                    "apellidos" => "Casas Nieto",
                    "curso" => "DAW 1",
                    "nota" => 5.7,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 42,
                    "nombre" => "Helena",
                    "apellidos" => "Cano Vidal",
                    "curso" => "ASIR 2",
                    "nota" => 8.7,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 43,
                    "nombre" => "Andrés",
                    "apellidos" => "Franco Ríos",
                    "curso" => "DAM 1",
                    "nota" => 4.1,
                    "estado" => "Suspenso"
                ],
                [
                    "id" => 44,
                    "nombre" => "Verónica",
                    "apellidos" => "Ortega Alba",
                    "curso" => "DAW 2",
                    "nota" => 6.8,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 45,
                    "nombre" => "Ismael",
                    "apellidos" => "León Méndez",
                    "curso" => "ASIR 1",
                    "nota" => 7.2,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 46,
                    "nombre" => "Eva",
                    "apellidos" => "Rubio Cuesta",
                    "curso" => "DAM 2",
                    "nota" => 9.6,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 47,
                    "nombre" => "Mateo",
                    "apellidos" => "Álvarez Bravo",
                    "curso" => "DAW 1",
                    "nota" => 3.0,
                    "estado" => "Suspenso"
                ],
                [
                    "id" => 48,
                    "nombre" => "Sofía",
                    "apellidos" => "Delgado Ríos",
                    "curso" => "ASIR 2",
                    "nota" => 5.3,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 49,
                    "nombre" => "Bruno",
                    "apellidos" => "Cortés Lara",
                    "curso" => "DAM 1",
                    "nota" => 6.6,
                    "estado" => "Aprobado"
                ],
                [
                    "id" => 50,
                    "nombre" => "Julia",
                    "apellidos" => "Peña Soria",
                    "curso" => "DAW 2",
                    "nota" => 4.7,
                    "estado" => "Suspenso"
                ]
            ];


            echo json_encode($alumnos, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
          },
    ]
];

$method = $_SERVER['REQUEST_METHOD'];
$path = $_SERVER['REQUEST_URI'];



$parsed = parse_url($path);
$cleanPath = $parsed['path'];

// Remove your project base path
$base = '/dam2526/Segundo/Sistemas%20de%20gesti%C3%B3n%20empresarial/003-Organizaci%C3%B3n%20y%20consulta%20de%20la%20informaci%C3%B3n/001-Definici%C3%B3n%20de%20campos/101-Ejercicios';
$finalPath = str_replace($base, '', $cleanPath);

if (empty($finalPath)) {
    $finalPath = '/';
}


if (isset($routes[$method][$finalPath])) {
    $routes[$method][$finalPath]();
} else {
    print_r(array_keys($routes['GET']));
    echo "<h2>404 - Route not found</h2>";
}