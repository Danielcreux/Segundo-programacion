<?php
// instalador.php
session_start();

// Configuración por defecto
$default_host = 'localhost';
$default_port = '3306';
$default_dbname = 'mi_base_datos';
$default_username = 'root';
$default_password = '';

// Procesar el formulario si se ha enviado
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['install'])) {
    // Obtener datos del formulario
    $host = $_POST['host'] ?? $default_host;
    $port = $_POST['port'] ?? $default_port;
    $dbname = $_POST['dbname'] ?? $default_dbname;
    $username = $_POST['username'] ?? $default_username;
    $password = $_POST['password'] ?? $default_password;
    
    // Verificar si se subió un archivo SQL
    $sql_file = null;
    if (isset($_FILES['sql_file']) && $_FILES['sql_file']['error'] === UPLOAD_ERR_OK) {
        $sql_file = $_FILES['sql_file']['tmp_name'];
    }
    
    // Guardar datos en sesión para mostrarlos después
    $_SESSION['form_data'] = [
        'host' => $host,
        'port' => $port,
        'dbname' => $dbname,
        'username' => $username,
        'password' => $password
    ];
    
    // Redirigir a la página de instalación
    header('Location: ' . $_SERVER['PHP_SELF'] . '?install=1');
    exit;
}

// Procesar la instalación si se ha solicitado
if (isset($_GET['install']) && isset($_SESSION['form_data'])) {
    $form_data = $_SESSION['form_data'];
    $host = $form_data['host'];
    $port = $form_data['port'];
    $dbname = $form_data['dbname'];
    $username = $form_data['username'];
    $password = $form_data['password'];
    
    // Conexión al servidor MySQL
    try {
        $pdo = new PDO("mysql:host=$host;port=$port", $username, $password);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        // Verificar si la base de datos ya existe
        $stmt = $pdo->query("SHOW DATABASES LIKE '$dbname'");
        $db_exists = $stmt->rowCount() > 0;
        
        if ($db_exists) {
            $progress[] = ["type" => "warning", "message" => "La base de datos '$dbname' ya existe."];
        } else {
            // Crear la base de datos
            $pdo->exec("CREATE DATABASE `$dbname` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
            $progress[] = ["type" => "success", "message" => "Base de datos '$dbname' creada correctamente."];
        }
        
        // Seleccionar la base de datos
        $pdo->exec("USE `$dbname`");
        $progress[] = ["type" => "info", "message" => "Conectado a la base de datos '$dbname'."];
        
        // Ejecutar archivo SQL si se proporcionó
        if (isset($_FILES['sql_file']) && $_FILES['sql_file']['error'] === UPLOAD_ERR_OK) {
            $sql_file = $_FILES['sql_file']['tmp_name'];
            $sql_content = file_get_contents($sql_file);
            
            // Dividir el contenido en consultas individuales
            $queries = array_filter(array_map('trim', explode(';', $sql_content)));
            
            foreach ($queries as $query) {
                if (!empty($query)) {
                    try {
                        $pdo->exec($query);
                        $progress[] = ["type" => "success", "message" => "Consulta ejecutada: " . substr($query, 0, 50) . "..."];
                    } catch (PDOException $e) {
                        $progress[] = ["type" => "danger", "message" => "Error en consulta: " . $e->getMessage()];
                    }
                }
            }
            
            $progress[] = ["type" => "success", "message" => "Archivo SQL importado correctamente."];
        }
        
        // Crear archivo de configuración
        $config_content = "<?php\n";
        $config_content .= "// Configuración de la base de datos\n";
        $config_content .= "define('DB_HOST', '$host');\n";
        $config_content .= "define('DB_PORT', '$port');\n";
        $config_content .= "define('DB_NAME', '$dbname');\n";
        $config_content .= "define('DB_USER', '$username');\n";
        $config_content .= "define('DB_PASS', '$password');\n";
        $config_content .= "?>";
        
        if (file_put_contents('config.php', $config_content)) {
            $progress[] = ["type" => "success", "message" => "Archivo de configuración creado correctamente."];
        } else {
            $progress[] = ["type" => "danger", "message" => "Error al crear el archivo de configuración."];
        }
        
        $progress[] = ["type" => "success", "message" => "Instalación completada correctamente."];
        
    } catch (PDOException $e) {
        $progress[] = ["type" => "danger", "message" => "Error de conexión: " . $e->getMessage()];
    }
    
    // Guardar progreso en sesión
    $_SESSION['install_progress'] = $progress;
    
    // Redirigir para evitar reenvío del formulario
    header('Location: ' . $_SERVER['PHP_SELF'] . '?result=1');
    exit;
}

// Obtener progreso de instalación si existe
$progress = $_SESSION['install_progress'] ?? [];
$form_data = $_SESSION['form_data'] ?? [
    'host' => $default_host,
    'port' => $default_port,
    'dbname' => $default_dbname,
    'username' => $default_username,
    'password' => $default_password
];

// Limpiar sesión después de mostrar resultados
if (isset($_GET['result'])) {
    unset($_SESSION['install_progress']);
    unset($_SESSION['form_data']);
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instalador de Base de Datos</title>
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3a0ca3;
            --success: #4cc9f0;
            --danger: #f72585;
            --warning: #fca311;
            --light: #f8f9fa;
            --dark: #212529;
            --gray: #6c757d;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 700px;
            overflow: hidden;
        }
        
        .header {
            background: var(--primary);
            color: white;
            padding: 25px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
        }
        
        .form-container {
            padding: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--dark);
        }
        
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.2);
        }
        
        .btn {
            display: inline-block;
            padding: 14px 28px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }
        
        .btn:hover {
            background: var(--secondary);
            transform: translateY(-2px);
        }
        
        .btn-block {
            display: block;
            width: 100%;
        }
        
        .progress-container {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .progress-item {
            padding: 12px 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid var(--gray);
        }
        
        .progress-item.success {
            background: rgba(76, 201, 240, 0.1);
            border-left-color: var(--success);
            color: #0a9396;
        }
        
        .progress-item.danger {
            background: rgba(247, 37, 133, 0.1);
            border-left-color: var(--danger);
            color: #ae2012;
        }
        
        .progress-item.warning {
            background: rgba(252, 163, 17, 0.1);
            border-left-color: var(--warning);
            color: #ee9b00;
        }
        
        .progress-item.info {
            background: rgba(67, 97, 238, 0.1);
            border-left-color: var(--primary);
            color: var(--primary);
        }
        
        .file-input {
            padding: 10px;
            border: 2px dashed #ced4da;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .file-input:hover {
            border-color: var(--primary);
            background: rgba(67, 97, 238, 0.05);
        }
        
        .form-row {
            display: flex;
            gap: 15px;
        }
        
        .form-row .form-group {
            flex: 1;
        }
        
        @media (max-width: 576px) {
            .form-row {
                flex-direction: column;
                gap: 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Instalador de Base de Datos</h1>
            <p>Complete la información para configurar su base de datos</p>
        </div>
        
        <div class="form-container">
            <form method="POST" action="<?php echo $_SERVER['PHP_SELF']; ?>" enctype="multipart/form-data">
                <div class="form-row">
                    <div class="form-group">
                        <label for="host">Host</label>
                        <input type="text" id="host" name="host" value="<?php echo htmlspecialchars($form_data['host']); ?>" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="port">Puerto (opcional)</label>
                        <input type="number" id="port" name="port" value="<?php echo htmlspecialchars($form_data['port']); ?>" placeholder="3306">
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="dbname">Nombre de Base de Datos</label>
                    <input type="text" id="dbname" name="dbname" value="<?php echo htmlspecialchars($form_data['dbname']); ?>" required>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="username">Usuario</label>
                        <input type="text" id="username" name="username" value="<?php echo htmlspecialchars($form_data['username']); ?>" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Contraseña</label>
                        <input type="password" id="password" name="password" value="<?php echo htmlspecialchars($form_data['password']); ?>">
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="sql_file">Archivo SQL (opcional)</label>
                    <div class="file-input">
                        <input type="file" id="sql_file" name="sql_file" accept=".sql">
                        <p>Haga clic aquí o arrastre un archivo SQL para importar</p>
                    </div>
                </div>
                
                <button type="submit" name="install" class="btn btn-block">Ejecutar Instalación</button>
            </form>
            
            <?php if (!empty($progress)): ?>
            <div class="progress-container">
                <h3>Progreso de la instalación:</h3>
                <?php foreach ($progress as $item): ?>
                <div class="progress-item <?php echo $item['type']; ?>">
                    <?php echo htmlspecialchars($item['message']); ?>
                </div>
                <?php endforeach; ?>
            </div>
            <?php endif; ?>
        </div>
    </div>

    <script>
        // Mejorar la experiencia de subida de archivos
        const fileInput = document.getElementById('sql_file');
        const fileInputContainer = fileInput.parentElement;
        
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileInputContainer.innerHTML = `<p>Archivo seleccionado: <strong>${this.files[0].name}</strong></p>`;
            }
        });
        
        // Permitir arrastrar y soltar archivos
        fileInputContainer.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.borderColor = '#4361ee';
            this.style.backgroundColor = 'rgba(67, 97, 238, 0.1)';
        });
        
        fileInputContainer.addEventListener('dragleave', function() {
            this.style.borderColor = '#ced4da';
            this.style.backgroundColor = 'transparent';
        });
        
        fileInputContainer.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.borderColor = '#ced4da';
            this.style.backgroundColor = 'transparent';
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                fileInputContainer.innerHTML = `<p>Archivo seleccionado: <strong>${e.dataTransfer.files[0].name}</strong></p>`;
            }
        });
    </script>
</body>
</html>