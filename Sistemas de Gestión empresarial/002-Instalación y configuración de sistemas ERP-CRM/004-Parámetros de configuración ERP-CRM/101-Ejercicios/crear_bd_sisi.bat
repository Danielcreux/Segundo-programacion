@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    CREACION DE BASE DE DATOS SISI
echo ========================================
echo.

:: Configuración
set "DB_NAME=sisi"
set "DB_USER=sisi"
set "DB_PASS=sisi"
set "MYSQL_HOST=127.0.0.1"
set "MYSQL_PORT=3306"

:: Verificar si MySQL está disponible
echo [1/5] Verificando conexión a MySQL...
mysql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: MySQL no encontrado en el PATH
    echo Asegúrate de que MySQL esté instalado y disponible
    pause
    exit /b 1
)

:: Solicitar contraseña de root
set /p "MYSQL_ROOT_PASS=Ingresa la contraseña de MySQL root (presiona Enter si no tiene): "

:: Crear archivo SQL temporal
echo [2/5] Creando script SQL temporal...
set "SQL_FILE=%temp%\crear_sisi_%random%.sql"

(
echo -- Script para crear la base de datos sisi con usuario y datos de ejemplo
echo -- Conectarse como root o usuario con privilegios de administración primero
echo.
echo -- Crear la base de datos si no existe
echo CREATE DATABASE IF NOT EXISTS `sisi` CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;
echo.
echo -- Crear el usuario si no existe y asignar privilegios
echo CREATE USER IF NOT EXISTS 'sisi'@'%%' IDENTIFIED BY 'sisi';
echo GRANT ALL PRIVILEGES ON `sisi`.* TO 'sisi'@'%%';
echo FLUSH PRIVILEGES;
echo.
echo -- Usar la base de datos
echo USE `sisi`;
echo.
echo -- Estructura de tabla para la tabla `alumnos`
echo CREATE TABLE IF NOT EXISTS `alumnos` (
echo   `Identificador` int(11) NOT NULL AUTO_INCREMENT,
echo   `Nombre` varchar(100) DEFAULT NULL,
echo   `Apellido 1` varchar(100) DEFAULT NULL,
echo   `Apellido 2` varchar(100) DEFAULT NULL,
echo   `Correo electrónico` varchar(100) DEFAULT NULL,
echo   `Teléfono` varchar(100) DEFAULT NULL,
echo   `Dirección` varchar(100) DEFAULT NULL,
echo   `Localidad` varchar(100) DEFAULT NULL,
echo   `Código postal` int(11) DEFAULT NULL,
echo   `DNI` varchar(100) DEFAULT NULL,
echo   `Apellidos del padre` varchar(100) DEFAULT NULL,
echo   `Email del padre` varchar(100) DEFAULT NULL,
echo   `Teléfono del padre` varchar(100) DEFAULT NULL,
echo   `Autorización imágenes` tinyint(4) DEFAULT NULL,
echo   `Autorización información a padres` tinyint(4) DEFAULT NULL,
echo   `Autorización salir del centro` tinyint(4) DEFAULT NULL,
echo   `NIA` varchar(100) DEFAULT NULL,
echo   `SIP` varchar(100) DEFAULT NULL,
echo   `Lugar donde se examina` varchar(100) DEFAULT NULL,
echo   `Fecha nacimiento` varchar(100) DEFAULT NULL,
echo   `Fotografía` mediumblob DEFAULT NULL,
echo   `Nombre de la madre` varchar(100) DEFAULT NULL,
echo   `Teléfono de la madre` varchar(100) DEFAULT NULL,
echo   `ALU` varchar(100) DEFAULT NULL,
echo   `Nacionalidad` varchar(100) DEFAULT NULL,
echo   `Sexo` varchar(100) DEFAULT NULL,
echo   `Correo electrónico de la madre` varchar(100) DEFAULT NULL,
echo   `Nombre del padre` varchar(100) DEFAULT NULL,
echo   PRIMARY KEY (`Identificador`)
echo ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
echo.
echo -- Estructura de tabla para la tabla `attendance`
echo CREATE TABLE IF NOT EXISTS `attendance` (
echo   `id` int(11) NOT NULL AUTO_INCREMENT,
echo   `module_code` varchar(255) NOT NULL,
echo   `student_id` int(11) NOT NULL,
echo   `present` tinyint(1) NOT NULL,
echo   `date` datetime NOT NULL,
echo   PRIMARY KEY (`id`)
echo ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
echo.
echo -- Estructura de tabla para la tabla `attendance2`
echo CREATE TABLE IF NOT EXISTS `attendance2` (
echo   `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
echo   `courseid` int(10) UNSIGNED DEFAULT NULL,
echo   `username` varchar(191) NOT NULL,
echo   `date` date NOT NULL,
echo   `time` char(5) NOT NULL,
echo   `present` tinyint(1) NOT NULL DEFAULT 0,
echo   `comment` text DEFAULT NULL,
echo   PRIMARY KEY (`id`),
echo   KEY `idx_user_date` (`username`,`date`),
echo   KEY `idx_att2_course_user` (`courseid`,`username`)
echo ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
echo.
echo -- Estructura de tabla para la tabla `calificaciones`
echo CREATE TABLE IF NOT EXISTS `calificaciones` (
echo   `id` int(11) NOT NULL AUTO_INCREMENT,
echo   `alumno_id` int(11) NOT NULL,
echo   `asignatura_code` varchar(255) NOT NULL,
echo   `calificacion` varchar(10) DEFAULT NULL,
echo   `period` varchar(20) NOT NULL DEFAULT 'DEFAULT-PERIOD',
echo   PRIMARY KEY (`id`),
echo   KEY `alumno_id` (`alumno_id`)
echo ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
echo.
echo -- Estructura de tabla para la tabla `calificaciones2`
echo CREATE TABLE IF NOT EXISTS `calificaciones2` (
echo   `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
echo   `courseid` int(10) UNSIGNED NOT NULL,
echo   `username` varchar(191) NOT NULL,
echo   `period` varchar(64) NOT NULL,
echo   `calificacion` tinyint(3) UNSIGNED DEFAULT NULL,
echo   PRIMARY KEY (`id`),
echo   UNIQUE KEY `uq_course_user_period` (`courseid`,`username`,`period`),
echo   KEY `idx_course_user` (`courseid`,`username`)
echo ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
echo.
echo -- Estructura de tabla para la tabla `documentos`
echo CREATE TABLE IF NOT EXISTS `documentos` (
echo   `id` int(11) NOT NULL AUTO_INCREMENT,
echo   `title` varchar(255) NOT NULL,
echo   `content` text DEFAULT NULL,
echo   `owner_id` int(11) NOT NULL,
echo   `created_at` timestamp NULL DEFAULT current_timestamp(),
echo   `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
echo   PRIMARY KEY (`id`)
echo ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
echo.
echo -- Estructura de tabla para la tabla `matriculas`
echo CREATE TABLE IF NOT EXISTS `matriculas` (
echo   `id` int(11) NOT NULL AUTO_INCREMENT,
echo   `alumno_id` int(11) NOT NULL,
echo   `role` enum('estudiante','profesor') NOT NULL,
echo   `cursos_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`cursos_json`)),
echo   `created_at` datetime NOT NULL DEFAULT current_timestamp(),
echo   PRIMARY KEY (`id`)
echo ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
echo.
echo -- Estructura de tabla para la tabla `mdl_course`
echo CREATE TABLE IF NOT EXISTS `mdl_course` (
echo   `id` bigint(10) NOT NULL AUTO_INCREMENT,
echo   `category` bigint(10) NOT NULL DEFAULT 0,
echo   `sortorder` bigint(10) NOT NULL DEFAULT 0,
echo   `fullname` varchar(1333) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
echo   `shortname` varchar(255) NOT NULL,
echo   `idnumber` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
echo   `summary` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
echo   `summaryformat` tinyint(2) NOT NULL DEFAULT 0,
echo   `format` varchar(21) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'topics',
echo   `showgrades` tinyint(2) NOT NULL DEFAULT 1,
echo   `newsitems` mediumint(5) NOT NULL DEFAULT 1,
echo   `startdate` bigint(10) NOT NULL DEFAULT 0,
echo   `enddate` bigint(10) NOT NULL DEFAULT 0,
echo   `relativedatesmode` tinyint(1) NOT NULL DEFAULT 0,
echo   `marker` bigint(10) NOT NULL DEFAULT 0,
echo   `maxbytes` bigint(10) NOT NULL DEFAULT 0,
echo   `legacyfiles` smallint(4) NOT NULL DEFAULT 0,
echo   `showreports` smallint(4) NOT NULL DEFAULT 0,
echo   `visible` tinyint(1) NOT NULL DEFAULT 1,
echo   `visibleold` tinyint(1) NOT NULL DEFAULT 1,
echo   `downloadcontent` tinyint(1) DEFAULT NULL,
echo   `groupmode` smallint(4) NOT NULL DEFAULT 0,
echo   `groupmodeforce` smallint(4) NOT NULL DEFAULT 0,
echo   `defaultgroupingid` bigint(10) NOT NULL DEFAULT 0,
echo   `lang` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
echo   `calendartype` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
echo   `theme` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
echo   `timecreated` bigint(10) NOT NULL DEFAULT 0,
echo   `timemodified` bigint(10) NOT NULL DEFAULT 0,
echo   `requested` tinyint(1) NOT NULL DEFAULT 0,
echo   `enablecompletion` tinyint(1) NOT NULL DEFAULT 0,
echo   `completionnotify` tinyint(1) NOT NULL DEFAULT 0,
echo   `cacherev` bigint(10) NOT NULL DEFAULT 0,
echo   `originalcourseid` bigint(10) DEFAULT NULL,
echo   `showactivitydates` tinyint(1) NOT NULL DEFAULT 0,
echo   `showcompletionconditions` tinyint(1) DEFAULT NULL,
echo   `pdfexportfont` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
echo   PRIMARY KEY (`id`),
echo   KEY `mdl_cour_cat_ix` (`category`),
echo   KEY `mdl_cour_idn_ix` (`idnumber`),
echo   KEY `mdl_cour_sho_ix` (`shortname`),
echo   KEY `mdl_cour_sor_ix` (`sortorder`),
echo   KEY `mdl_cour_ori_ix` (`originalcourseid`)
echo ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci COMMENT='Central course table' ROW_FORMAT=COMPRESSED;
echo.
echo -- Estructura de tabla para la tabla `profesorado`
echo CREATE TABLE IF NOT EXISTS `profesorado` (
echo   `id` int(11) NOT NULL AUTO_INCREMENT,
echo   `profesor_id` int(11) NOT NULL,
echo   `rol` varchar(50) NOT NULL DEFAULT 'profesor',
echo   `cursos_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`cursos_json`)),
echo   `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
echo   PRIMARY KEY (`id`),
echo   UNIQUE KEY `uniq_profesor` (`profesor_id`)
echo ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
echo.
echo -- Estructura de tabla para la tabla `profesores`
echo CREATE TABLE IF NOT EXISTS `profesores` (
echo   `id` int(11) NOT NULL AUTO_INCREMENT,
echo   `DNI` varchar(200) NOT NULL,
echo   `Nombre` varchar(100) DEFAULT NULL,
echo   `Apellido1` varchar(100) DEFAULT NULL,
echo   `Apellido2` varchar(255) DEFAULT NULL,
echo   `email` varchar(100) DEFAULT NULL,
echo   PRIMARY KEY (`id`)
echo ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
echo.
echo -- Estructura de tabla para la tabla `tutorias`
echo CREATE TABLE IF NOT EXISTS `tutorias` (
echo   `id` int(11) NOT NULL AUTO_INCREMENT,
echo   `profesor_id` int(11) NOT NULL,
echo   `role` varchar(50) NOT NULL,
echo   `cursos_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`cursos_json`)),
echo   `created_at` timestamp NULL DEFAULT current_timestamp(),
echo   PRIMARY KEY (`id`),
echo   KEY `profesor_id` (`profesor_id`)
echo ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
echo.
echo -- Estructura de tabla para la tabla `usuarios`
echo CREATE TABLE IF NOT EXISTS `usuarios` (
echo   `Identificador` int(11) NOT NULL AUTO_INCREMENT,
echo   `usuario` varchar(20) NOT NULL,
echo   `contrasena` varchar(20) NOT NULL,
echo   `nombre` varchar(20) NOT NULL,
echo   `apellido1` varchar(20) NOT NULL,
echo   `apellido2` varchar(20) NOT NULL,
echo   `perfil` enum('direccion','docentes','secretaria','') NOT NULL,
echo   `email` varchar(255) NOT NULL,
echo   PRIMARY KEY (`Identificador`)
echo ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
echo.
echo -- Estructura para la vista `vista_duplicados`
echo CREATE OR REPLACE VIEW `vista_duplicados` AS
echo SELECT 
echo     `a1`.`id` AS `id_1`,
echo     `a1`.`courseid` AS `courseid`,
echo     `a1`.`username` AS `username`,
echo     `a1`.`date` AS `date`,
echo     `a1`.`time` AS `time_1`,
echo     `a2`.`id` AS `id_2`,
echo     `a2`.`time` AS `time_2`,
echo     ABS(TIMESTAMPDIFF(MINUTE,
echo         STR_TO_DATE(CONCAT(`a1`.`date`, ' ', `a1`.`time`), '%%Y-%%m-%%d %%H:%%i'),
echo         STR_TO_DATE(CONCAT(`a2`.`date`, ' ', `a2`.`time`), '%%Y-%%m-%%d %%H:%%i'))) AS `diff_min`
echo FROM
echo     (`attendance2` `a1`
echo     JOIN `attendance2` `a2` ON ((`a1`.`courseid` = `a2`.`courseid`
echo         AND `a1`.`username` = `a2`.`username`
echo         AND `a1`.`date` = `a2`.`date`
echo         AND `a1`.`id` < `a2`.`id`)))
echo WHERE
echo     ABS(TIMESTAMPDIFF(MINUTE,
echo         STR_TO_DATE(CONCAT(`a1`.`date`, ' ', `a1`.`time`), '%%Y-%%m-%%d %%H:%%i'),
echo         STR_TO_DATE(CONCAT(`a2`.`date`, ' ', `a2`.`time`), '%%Y-%%m-%%d %%H:%%i'))) < 5
echo ORDER BY `a1`.`courseid` , `a1`.`username` , `a1`.`date` , `a1`.`time` , `a2`.`time`;
echo.
echo -- Insertar datos de ejemplo
echo.
echo -- Insertar alumnos
echo INSERT INTO `alumnos` (`Identificador`, `Nombre`, `Apellido 1`, `Apellido 2`, `Correo electrónico`, `Teléfono`, `Dirección`, `Localidad`, `Código postal`, `DNI`, `Apellidos del padre`, `Email del padre`, `Teléfono del padre`, `Autorización imágenes`, `Autorización información a padres`, `Autorización salir del centro`, `NIA`, `SIP`, `Lugar donde se examina`, `Fecha nacimiento`, `Fotografía`, `Nombre de la madre`, `Teléfono de la madre`, `ALU`, `Nacionalidad`, `Sexo`, `Correo electrónico de la madre`, `Nombre del padre`) VALUES
echo (1, 'María', 'García', 'López', 'maria.garcia@email.com', '612345678', 'Calle Mayor 123', 'Madrid', 28001, '12345678A', 'García Rodríguez', 'padre.garcia@email.com', '611223344', 1, 1, 1, 'NIA001', 'SIP001', 'Aula 101', '2005-03-15', NULL, 'Ana López Martínez', '633445566', 'ALU001', 'Española', 'Femenino', 'madre.lopez@email.com', 'Carlos García Rodríguez'),
echo (2, 'Carlos', 'Martínez', 'Sánchez', 'carlos.martinez@email.com', '623456789', 'Avenida Libertad 45', 'Barcelona', 8001, '23456789B', 'Martínez Fernández', 'padre.martinez@email.com', '622334455', 1, 0, 1, 'NIA002', 'SIP002', 'Aula 102', '2005-07-22', NULL, 'Elena Sánchez Ruiz', '644556677', 'ALU002', 'Española', 'Masculino', 'madre.sanchez@email.com', 'Javier Martínez Fernández'),
echo (3, 'Laura', 'Fernández', 'Gómez', 'laura.fernandez@email.com', '634567890', 'Plaza España 67', 'Valencia', 46001, '34567890C', 'Fernández López', 'padre.fernandez@email.com', '633445566', 0, 1, 0, 'NIA003', 'SIP003', 'Aula 103', '2006-01-10', NULL, 'Marta Gómez Pérez', '655667788', 'ALU003', 'Española', 'Femenino', 'madre.gomez@email.com', 'David Fernández López');
echo.
echo -- Insertar profesores
echo INSERT INTO `profesores` (`id`, `DNI`, `Nombre`, `Apellido1`, `Apellido2`, `email`) VALUES
echo (1, '87654321X', 'Ana', 'Rodríguez', 'Pérez', 'ana.rodriguez@colegio.edu'),
echo (2, '76543221Y', 'Pedro', 'Gómez', 'Martínez', 'pedro.gomez@colegio.edu'),
echo (3, '65432132Z', 'Elena', 'Sánchez', 'Fernández', 'elena.sanchez@colegio.edu');
echo.
echo -- Insertar usuarios del sistema
echo INSERT INTO `usuarios` (`Identificador`, `usuario`, `contrasena`, `nombre`, `apellido1`, `apellido2`, `perfil`, `email`) VALUES
echo (1, 'admin', 'admin123', 'Juan', 'Administrador', 'Sistema', 'direccion', 'juan.admin@colegio.edu'),
echo (2, 'profe_ana', 'profe123', 'Ana', 'Rodríguez', 'Pérez', 'docentes', 'ana.rodriguez@colegio.edu'),
echo (3, 'secretaria1', 'secre123', 'María', 'López', 'García', 'secretaria', 'maria.lopez@colegio.edu');
echo.
echo -- Insertar cursos
echo INSERT INTO `mdl_course` (`id`, `category`, `sortorder`, `fullname`, `shortname`, `idnumber`, `summary`, `summaryformat`, `format`, `showgrades`, `newsitems`, `startdate`, `enddate`, `relativedatesmode`, `marker`, `maxbytes`, `legacyfiles`, `showreports`, `visible`, `visibleold`, `downloadcontent`, `groupmode`, `groupmodeforce`, `defaultgroupingid`, `lang`, `calendartype`, `theme`, `timecreated`, `timemodified`, `requested`, `enablecompletion`, `completionnotify`, `cacherev`, `originalcourseid`, `showactivitydates`, `showcompletionconditions`, `pdfexportfont`) VALUES
echo (1, 1, 1, 'Matemáticas Avanzadas', 'MAT101', 'MAT101', 'Curso de matemáticas para primer año de bachillerato', 1, 'topics', 1, 5, 1732406400, 1763942400, 0, 0, 0, 0, 0, 1, 1, NULL, 0, 0, 0, 'es', 'gregorian', '', 1732406400, 1732406400, 0, 0, 0, 0, NULL, 0, NULL, NULL),
echo (2, 1, 2, 'Lengua y Literatura', 'LEN201', 'LEN201', 'Curso de lengua y literatura española', 1, 'topics', 1, 5, 1732406400, 1763942400, 0, 0, 0, 0, 0, 1, 1, NULL, 0, 0, 0, 'es', 'gregorian', '', 1732406400, 1732406400, 0, 0, 0, 0, NULL, 0, NULL, NULL),
echo (3, 2, 3, 'Inglés Avanzado', 'ING301', 'ING301', 'Curso de inglés nivel avanzado', 1, 'topics', 1, 5, 1732406400, 1763942400, 0, 0, 0, 0, 0, 1, 1, NULL, 0, 0, 0, 'es', 'gregorian', '', 1732406400, 1732406400, 0, 0, 0, 0, NULL, 0, NULL, NULL);
echo.
echo -- Insertar matrículas
echo INSERT INTO `matriculas` (`id`, `alumno_id`, `role`, `cursos_json`, `created_at`) VALUES
echo (1, 1, 'estudiante', '[\"MAT101\", \"LEN201\", \"ING301\"]', '2025-10-24 19:42:26'),
echo (2, 2, 'estudiante', '[\"MAT101\", \"LEN201\", \"FIS202\"]', '2025-10-24 19:42:26'),
echo (3, 3, 'estudiante', '[\"MAT101\", \"LEN201\", \"QUI203\"]', '2025-10-24 19:42:26');
echo.
echo -- Insertar profesorado
echo INSERT INTO `profesorado` (`id`, `profesor_id`, `rol`, `cursos_json`, `updated_at`) VALUES
echo (1, 1, 'profesor', '[\"MAT101\", \"MAT102\"]', '2025-10-24 17:42:26'),
echo (2, 2, 'tutor', '[\"LEN201\", \"LEN202\"]', '2025-10-24 17:42:26'),
echo (3, 3, 'profesor', '[\"ING301\", \"ING302\"]', '2025-10-24 17:42:26');
echo.
echo -- Insertar tutorías
echo INSERT INTO `tutorias` (`id`, `profesor_id`, `role`, `cursos_json`, `created_at`) VALUES
echo (1, 1, 'tutor', '[\"1A\", \"1B\"]', '2025-10-24 17:42:26'),
echo (2, 2, 'tutor', '[\"2A\", \"2B\"]', '2025-10-24 17:42:26'),
echo (3, 3, 'tutor', '[\"3A\", \"3B\"]', '2025-10-24 17:42:26');
echo.
echo -- Insertar asistencias
echo INSERT INTO `attendance` (`id`, `module_code`, `student_id`, `present`, `date`) VALUES
echo (1, 'MAT101', 1, 1, '2025-10-24 08:00:00'),
echo (2, 'MAT101', 2, 1, '2025-10-24 08:00:00'),
echo (3, 'MAT101', 3, 0, '2025-10-24 08:00:00'),
echo (4, 'LEN201', 1, 1, '2025-10-24 10:00:00'),
echo (5, 'LEN201', 2, 1, '2025-10-24 10:00:00'),
echo (6, 'LEN201', 3, 1, '2025-10-24 10:00:00');
echo.
echo -- Insertar asistencias2
echo INSERT INTO `attendance2` (`id`, `courseid`, `username`, `date`, `time`, `present`, `comment`) VALUES
echo (1, 1, 'maria.garcia', '2025-10-24', '08:00', 1, 'Puntual'),
echo (2, 1, 'carlos.martinez', '2025-10-24', '08:00', 1, 'Puntual'),
echo (3, 1, 'laura.fernandez', '2025-10-24', '08:00', 0, 'Ausente justificada'),
echo (4, 2, 'maria.garcia', '2025-10-24', '10:00', 1, NULL),
echo (5, 2, 'carlos.martinez', '2025-10-24', '10:00', 1, NULL),
echo (6, 2, 'laura.fernandez', '2025-10-24', '10:00', 1, NULL);
echo.
echo -- Insertar calificaciones
echo INSERT INTO `calificaciones` (`id`, `alumno_id`, `asignatura_code`, `calificacion`, `period`) VALUES
echo (1, 1, 'MAT101', '8.5', 'Q1-2025'),
echo (2, 1, 'LEN201', '9.0', 'Q1-2025'),
echo (3, 2, 'MAT101', '7.2', 'Q1-2025'),
echo (4, 2, 'LEN201', '8.8', 'Q1-2025'),
echo (5, 3, 'MAT101', '6.5', 'Q1-2025'),
echo (6, 3, 'LEN201', '9.5', 'Q1-2025');
echo.
echo -- Insertar calificaciones2
echo INSERT INTO `calificaciones2` (`id`, `courseid`, `username`, `period`, `calificacion`) VALUES
echo (1, 1, 'maria.garcia', 'Q1-2025', 85),
echo (2, 2, 'maria.garcia', 'Q1-2025', 90),
echo (3, 1, 'carlos.martinez', 'Q1-2025', 72),
echo (4, 2, 'carlos.martinez', 'Q1-2025', 88),
echo (5, 1, 'laura.fernandez', 'Q1-2025', 65),
echo (6, 2, 'laura.fernandez', 'Q1-2025', 95);
echo.
echo -- Insertar documentos
echo INSERT INTO `documentos` (`id`, `title`, `content`, `owner_id`, `created_at`, `updated_at`) VALUES
echo (1, 'Planificación Anual Matemáticas', 'Contenido del plan de estudios de matemáticas para el curso 2024-2025...', 1, '2025-10-24 17:42:26', '2025-10-24 17:42:26'),
echo (2, 'Reglamento Interno', 'Normas y procedimientos del centro educativo...', 2, '2025-10-24 17:42:26', '2025-10-24 17:42:26'),
echo (3, 'Actividades Extraescolares', 'Programación de actividades complementarias...', 1, '2025-10-24 17:42:26', '2025-10-24 17:42:26');
echo.
echo -- Añadir restricciones de clave foránea
echo ALTER TABLE `calificaciones`
echo   ADD CONSTRAINT `calificaciones_ibfk_1` FOREIGN KEY (`alumno_id`) REFERENCES `alumnos` (`Identificador`);
echo.
echo ALTER TABLE `tutorias`
echo   ADD CONSTRAINT `tutorias_ibfk_1` FOREIGN KEY (`profesor_id`) REFERENCES `profesores` (`id`);
echo.
echo -- Mostrar mensaje de confirmación
echo SELECT 'Base de datos sisi creada exitosamente con datos de ejemplo' AS 'Estado';
) > "%SQL_FILE%"

:: Ejecutar el script SQL
echo [3/5] Ejecutando script SQL...
if "%MYSQL_ROOT_PASS%"=="" (
    mysql -h %MYSQL_HOST% -P %MYSQL_PORT% -u root < "%SQL_FILE%"
) else (
    mysql -h %MYSQL_HOST% -P %MYSQL_PORT% -u root -p%MYSQL_ROOT_PASS% < "%SQL_FILE%"
)

if %errorlevel% equ 0 (
    echo [4/5] ¡Base de datos creada exitosamente!
) else (
    echo [4/5] ERROR: No se pudo crear la base de datos
    echo Revisa la contraseña de root y que MySQL esté ejecutándose
    del "%SQL_FILE%"
    pause
    exit /b 1
)

:: Limpiar archivo temporal
del "%SQL_FILE%"

:: Verificar la creación
echo [5/5] Verificando la creación...
if "%MYSQL_ROOT_PASS%"=="" (
    mysql -h %MYSQL_HOST% -P %MYSQL_PORT% -u root -e "USE sisi; SHOW TABLES; SELECT COUNT(*) as total_alumnos FROM alumnos;"
) else (
    mysql -h %MYSQL_HOST% -P %MYSQL_PORT% -u root -p%MYSQL_ROOT_PASS% -e "USE sisi; SHOW TABLES; SELECT COUNT(*) as total_alumnos FROM alumnos;"
)

echo.
echo ========================================
echo    CONFIGURACIÓN COMPLETADA
echo ========================================
echo.
echo Base de datos: sisi
echo Usuario: sisi
echo Contraseña: sisi
echo.
echo Ahora puedes ejecutar tu aplicación Flask
echo.
pause