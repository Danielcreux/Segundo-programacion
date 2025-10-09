<?php
header('Content-Type: application/json');

// Validar que existe el parámetro ruta
if (!isset($_GET['ruta'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Parámetro "ruta" requerido']);
    exit;
}

// Validar y sanitizar la ruta
$ruta = filter_var($_GET['ruta'], FILTER_SANITIZE_STRING);
$rutasPermitidas = ['categorias', 'aplicaciones'];

if (!in_array($ruta, $rutasPermitidas)) {
    http_response_code(404);
    echo json_encode(['error' => 'Ruta no encontrada']);
    exit;
}

try {
    require "config.php";
    
    // Verificar conexión a la base de datos
    if (!$db) {
        throw new Exception('Error de conexión a la base de datos');
    }
    
    // Determinar la consulta según la ruta
    $consultas = [
        'categorias' => 'SELECT * FROM categorias_aplicaciones',
        'aplicaciones' => 'SELECT * FROM aplicaciones'
    ];
    
    $stmt = $db->prepare($consultas[$ruta]);
    $stmt->execute();
    
    $result = $stmt->fetchAll(PDO::FETCH_ASSOC); // Corregí "db::FETCH_ASSOC"
    
    if (empty($result)) {
        http_response_code(404);
        echo json_encode(['message' => 'No se encontraron registros']);
        exit;
    }
    
    echo json_encode($result, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Error en la base de datos: ' . $e->getMessage()]);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
?>