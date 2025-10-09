<?php
    session_start();
// iniciarsesion.php - Procesar inicio de sesión

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// Incluir configuración de la base de datos
require_once 'config.php';

// Obtener datos del request
$input = json_decode(file_get_contents('php://input'), true);

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode([
        'success' => false,
        'message' => 'Método no permitido'
    ]);
    exit;
}

if (!$input || !isset($input['usuario']) || !isset($input['contrasena'])) {
    echo json_encode([
        'success' => false,
        'message' => 'Datos incompletos'
    ]);
    exit;
}

$usuario = trim($input['usuario']);
$contrasena = trim($input['contrasena']);

// Conectar a la base de datos
$database = new Database();
$db = $database->getConnection();

if (!$db) {
    echo json_encode([
        'success' => false,
        'message' => 'Error de conexión a la base de datos'
    ]);
    exit;
}

try {
    // Preparar la consulta para buscar el usuario según tu estructura
    $query = "SELECT Identificador, usuario, contrasena, nombrecompleto 
              FROM usuarios 
              WHERE usuario = :usuario";
    $stmt = $db->prepare($query);
    $stmt->bindParam(':usuario', $usuario);
    $stmt->execute();

    if ($stmt->rowCount() > 0) {
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        
        // Verificar la contraseña (comparación directa según tu estructura)
        if ($contrasena === $row['contrasena']) {
            
             $_SESSION['usuario'] = $row['nombrecompleto'];
             $_SESSION['user_id'] = $row['Identificador'];
             $_SESSION['username'] = $row['usuario'];
            echo json_encode([
                'success' => true,
                'message' => 'Login exitoso',
                'usuario' => $row['usuario'],
                'user_id' => $row['Identificador'],
                'nombre_completo' => $row['nombrecompleto']
            ]);
        } else {
            echo json_encode([
                'success' => false,
                'message' => 'Contraseña incorrecta'
            ]);
        }
    } else {
        echo json_encode([
            'success' => false,
            'message' => 'Usuario no encontrado'
        ]);
    }
} catch (PDOException $exception) {
    echo json_encode([
        'success' => false,
        'message' => 'Error en la consulta: ' . $exception->getMessage()
    ]);
}
?>