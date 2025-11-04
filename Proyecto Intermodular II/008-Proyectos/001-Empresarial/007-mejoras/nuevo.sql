-- Script para crear la base de datos sisi con usuario y datos de ejemplo
-- Conectarse como root o usuario con privilegios de administración primero

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS `sisi` CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;

-- Crear el usuario si no existe y asignar privilegios
CREATE USER IF NOT EXISTS 'sisi'@'%' IDENTIFIED BY 'sisi';
GRANT ALL PRIVILEGES ON `sisi`.* TO 'sisi'@'%';
FLUSH PRIVILEGES;

-- Usar la base de datos
USE `sisi`;

-- Estructura de tabla para la tabla `alumnos`
CREATE TABLE IF NOT EXISTS `alumnos` (
  `Identificador` int(11) NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) DEFAULT NULL,
  `Apellido 1` varchar(100) DEFAULT NULL,
  `Apellido 2` varchar(100) DEFAULT NULL,
  `Correo electrónico` varchar(100) DEFAULT NULL,
  `Teléfono` varchar(100) DEFAULT NULL,
  `Dirección` varchar(100) DEFAULT NULL,
  `Localidad` varchar(100) DEFAULT NULL,
  `Código postal` int(11) DEFAULT NULL,
  `DNI` varchar(100) DEFAULT NULL,
  `Apellidos del padre` varchar(100) DEFAULT NULL,
  `Email del padre` varchar(100) DEFAULT NULL,
  `Teléfono del padre` varchar(100) DEFAULT NULL,
  `Autorización imágenes` tinyint(4) DEFAULT NULL,
  `Autorización información a padres` tinyint(4) DEFAULT NULL,
  `Autorización salir del centro` tinyint(4) DEFAULT NULL,
  `NIA` varchar(100) DEFAULT NULL,
  `SIP` varchar(100) DEFAULT NULL,
  `Lugar donde se examina` varchar(100) DEFAULT NULL,
  `Fecha nacimiento` varchar(100) DEFAULT NULL,
  `Fotografía` mediumblob DEFAULT NULL,
  `Nombre de la madre` varchar(100) DEFAULT NULL,
  `Teléfono de la madre` varchar(100) DEFAULT NULL,
  `ALU` varchar(100) DEFAULT NULL,
  `Nacionalidad` varchar(100) DEFAULT NULL,
  `Sexo` varchar(100) DEFAULT NULL,
  `Correo electrónico de la madre` varchar(100) DEFAULT NULL,
  `Nombre del padre` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Identificador`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- Estructura de tabla para la tabla `attendance`
CREATE TABLE IF NOT EXISTS `attendance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `module_code` varchar(255) NOT NULL,
  `student_id` int(11) NOT NULL,
  `present` tinyint(1) NOT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- Estructura de tabla para la tabla `attendance2`
CREATE TABLE IF NOT EXISTS `attendance2` (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `courseid` int(10) UNSIGNED DEFAULT NULL,
  `username` varchar(191) NOT NULL,
  `date` date NOT NULL,
  `time` char(5) NOT NULL,
  `present` tinyint(1) NOT NULL DEFAULT 0,
  `comment` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user_date` (`username`,`date`),
  KEY `idx_att2_course_user` (`courseid`,`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Estructura de tabla para la tabla `calificaciones`
CREATE TABLE IF NOT EXISTS `calificaciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alumno_id` int(11) NOT NULL,
  `asignatura_code` varchar(255) NOT NULL,
  `calificacion` varchar(10) DEFAULT NULL,
  `period` varchar(20) NOT NULL DEFAULT 'DEFAULT-PERIOD',
  PRIMARY KEY (`id`),
  KEY `alumno_id` (`alumno_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- Estructura de tabla para la tabla `calificaciones2`
CREATE TABLE IF NOT EXISTS `calificaciones2` (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `courseid` int(10) UNSIGNED NOT NULL,
  `username` varchar(191) NOT NULL,
  `period` varchar(64) NOT NULL,
  `calificacion` tinyint(3) UNSIGNED DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_course_user_period` (`courseid`,`username`,`period`),
  KEY `idx_course_user` (`courseid`,`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Estructura de tabla para la tabla `documentos`
CREATE TABLE IF NOT EXISTS `documentos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `content` text DEFAULT NULL,
  `owner_id` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- Estructura de tabla para la tabla `matriculas`
CREATE TABLE IF NOT EXISTS `matriculas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alumno_id` int(11) NOT NULL,
  `role` enum('estudiante','profesor') NOT NULL,
  `cursos_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`cursos_json`)),
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- Estructura de tabla para la tabla `mdl_course`
CREATE TABLE IF NOT EXISTS `mdl_course` (
  `id` bigint(10) NOT NULL AUTO_INCREMENT,
  `category` bigint(10) NOT NULL DEFAULT 0,
  `sortorder` bigint(10) NOT NULL DEFAULT 0,
  `fullname` varchar(1333) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `shortname` varchar(255) NOT NULL,
  `idnumber` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `summary` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `summaryformat` tinyint(2) NOT NULL DEFAULT 0,
  `format` varchar(21) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'topics',
  `showgrades` tinyint(2) NOT NULL DEFAULT 1,
  `newsitems` mediumint(5) NOT NULL DEFAULT 1,
  `startdate` bigint(10) NOT NULL DEFAULT 0,
  `enddate` bigint(10) NOT NULL DEFAULT 0,
  `relativedatesmode` tinyint(1) NOT NULL DEFAULT 0,
  `marker` bigint(10) NOT NULL DEFAULT 0,
  `maxbytes` bigint(10) NOT NULL DEFAULT 0,
  `legacyfiles` smallint(4) NOT NULL DEFAULT 0,
  `showreports` smallint(4) NOT NULL DEFAULT 0,
  `visible` tinyint(1) NOT NULL DEFAULT 1,
  `visibleold` tinyint(1) NOT NULL DEFAULT 1,
  `downloadcontent` tinyint(1) DEFAULT NULL,
  `groupmode` smallint(4) NOT NULL DEFAULT 0,
  `groupmodeforce` smallint(4) NOT NULL DEFAULT 0,
  `defaultgroupingid` bigint(10) NOT NULL DEFAULT 0,
  `lang` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `calendartype` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `theme` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `timecreated` bigint(10) NOT NULL DEFAULT 0,
  `timemodified` bigint(10) NOT NULL DEFAULT 0,
  `requested` tinyint(1) NOT NULL DEFAULT 0,
  `enablecompletion` tinyint(1) NOT NULL DEFAULT 0,
  `completionnotify` tinyint(1) NOT NULL DEFAULT 0,
  `cacherev` bigint(10) NOT NULL DEFAULT 0,
  `originalcourseid` bigint(10) DEFAULT NULL,
  `showactivitydates` tinyint(1) NOT NULL DEFAULT 0,
  `showcompletionconditions` tinyint(1) DEFAULT NULL,
  `pdfexportfont` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mdl_cour_cat_ix` (`category`),
  KEY `mdl_cour_idn_ix` (`idnumber`),
  KEY `mdl_cour_sho_ix` (`shortname`),
  KEY `mdl_cour_sor_ix` (`sortorder`),
  KEY `mdl_cour_ori_ix` (`originalcourseid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci COMMENT='Central course table' ROW_FORMAT=COMPRESSED;

-- Estructura de tabla para la tabla `profesorado`
CREATE TABLE IF NOT EXISTS `profesorado` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `profesor_id` int(11) NOT NULL,
  `rol` varchar(50) NOT NULL DEFAULT 'profesor',
  `cursos_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`cursos_json`)),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_profesor` (`profesor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Estructura de tabla para la tabla `profesores`
CREATE TABLE IF NOT EXISTS `profesores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `DNI` varchar(200) NOT NULL,
  `Nombre` varchar(100) DEFAULT NULL,
  `Apellido1` varchar(100) DEFAULT NULL,
  `Apellido2` varchar(255) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- Estructura de tabla para la tabla `tutorias`
CREATE TABLE IF NOT EXISTS `tutorias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `profesor_id` int(11) NOT NULL,
  `role` varchar(50) NOT NULL,
  `cursos_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`cursos_json`)),
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `profesor_id` (`profesor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- Estructura de tabla para la tabla `usuarios`
CREATE TABLE IF NOT EXISTS `usuarios` (
  `Identificador` int(11) NOT NULL AUTO_INCREMENT,
  `usuario` varchar(20) NOT NULL,
  `contrasena` varchar(20) NOT NULL,
  `nombre` varchar(20) NOT NULL,
  `apellido1` varchar(20) NOT NULL,
  `apellido2` varchar(20) NOT NULL,
  `perfil` enum('direccion','docentes','secretaria','') NOT NULL,
  `email` varchar(255) NOT NULL,
  PRIMARY KEY (`Identificador`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- Estructura para la vista `vista_duplicados`
CREATE OR REPLACE VIEW `vista_duplicados` AS
SELECT 
    `a1`.`id` AS `id_1`,
    `a1`.`courseid` AS `courseid`,
    `a1`.`username` AS `username`,
    `a1`.`date` AS `date`,
    `a1`.`time` AS `time_1`,
    `a2`.`id` AS `id_2`,
    `a2`.`time` AS `time_2`,
    ABS(TIMESTAMPDIFF(MINUTE,
        STR_TO_DATE(CONCAT(`a1`.`date`, ' ', `a1`.`time`), '%Y-%m-%d %H:%i'),
        STR_TO_DATE(CONCAT(`a2`.`date`, ' ', `a2`.`time`), '%Y-%m-%d %H:%i'))) AS `diff_min`
FROM
    (`attendance2` `a1`
    JOIN `attendance2` `a2` ON ((`a1`.`courseid` = `a2`.`courseid`
        AND `a1`.`username` = `a2`.`username`
        AND `a1`.`date` = `a2`.`date`
        AND `a1`.`id` < `a2`.`id`)))
WHERE
    ABS(TIMESTAMPDIFF(MINUTE,
        STR_TO_DATE(CONCAT(`a1`.`date`, ' ', `a1`.`time`), '%Y-%m-%d %H:%i'),
        STR_TO_DATE(CONCAT(`a2`.`date`, ' ', `a2`.`time`), '%Y-%m-%d %H:%i'))) < 5
ORDER BY `a1`.`courseid` , `a1`.`username` , `a1`.`date` , `a1`.`time` , `a2`.`time`;

-- Insertar datos de ejemplo

-- Insertar alumnos
INSERT INTO `alumnos` (`Identificador`, `Nombre`, `Apellido 1`, `Apellido 2`, `Correo electrónico`, `Teléfono`, `Dirección`, `Localidad`, `Código postal`, `DNI`, `Apellidos del padre`, `Email del padre`, `Teléfono del padre`, `Autorización imágenes`, `Autorización información a padres`, `Autorización salir del centro`, `NIA`, `SIP`, `Lugar donde se examina`, `Fecha nacimiento`, `Fotografía`, `Nombre de la madre`, `Teléfono de la madre`, `ALU`, `Nacionalidad`, `Sexo`, `Correo electrónico de la madre`, `Nombre del padre`) VALUES
(1, 'María', 'García', 'López', 'maria.garcia@email.com', '612345678', 'Calle Mayor 123', 'Madrid', 28001, '12345678A', 'García Rodríguez', 'padre.garcia@email.com', '611223344', 1, 1, 1, 'NIA001', 'SIP001', 'Aula 101', '2005-03-15', NULL, 'Ana López Martínez', '633445566', 'ALU001', 'Española', 'Femenino', 'madre.lopez@email.com', 'Carlos García Rodríguez'),
(2, 'Carlos', 'Martínez', 'Sánchez', 'carlos.martinez@email.com', '623456789', 'Avenida Libertad 45', 'Barcelona', 8001, '23456789B', 'Martínez Fernández', 'padre.martinez@email.com', '622334455', 1, 0, 1, 'NIA002', 'SIP002', 'Aula 102', '2005-07-22', NULL, 'Elena Sánchez Ruiz', '644556677', 'ALU002', 'Española', 'Masculino', 'madre.sanchez@email.com', 'Javier Martínez Fernández'),
(3, 'Laura', 'Fernández', 'Gómez', 'laura.fernandez@email.com', '634567890', 'Plaza España 67', 'Valencia', 46001, '34567890C', 'Fernández López', 'padre.fernandez@email.com', '633445566', 0, 1, 0, 'NIA003', 'SIP003', 'Aula 103', '2006-01-10', NULL, 'Marta Gómez Pérez', '655667788', 'ALU003', 'Española', 'Femenino', 'madre.gomez@email.com', 'David Fernández López');

-- Insertar profesores
INSERT INTO `profesores` (`id`, `DNI`, `Nombre`, `Apellido1`, `Apellido2`, `email`) VALUES
(1, '87654321X', 'Ana', 'Rodríguez', 'Pérez', 'ana.rodriguez@colegio.edu'),
(2, '76543221Y', 'Pedro', 'Gómez', 'Martínez', 'pedro.gomez@colegio.edu'),
(3, '65432132Z', 'Elena', 'Sánchez', 'Fernández', 'elena.sanchez@colegio.edu');

-- Insertar usuarios del sistema
INSERT INTO `usuarios` (`Identificador`, `usuario`, `contrasena`, `nombre`, `apellido1`, `apellido2`, `perfil`, `email`) VALUES
(1, 'admin', 'admin123', 'Juan', 'Administrador', 'Sistema', 'direccion', 'juan.admin@colegio.edu'),
(2, 'profe_ana', 'profe123', 'Ana', 'Rodríguez', 'Pérez', 'docentes', 'ana.rodriguez@colegio.edu'),
(3, 'secretaria1', 'secre123', 'María', 'López', 'García', 'secretaria', 'maria.lopez@colegio.edu');

-- Insertar cursos
INSERT INTO `mdl_course` (`id`, `category`, `sortorder`, `fullname`, `shortname`, `idnumber`, `summary`, `summaryformat`, `format`, `showgrades`, `newsitems`, `startdate`, `enddate`, `relativedatesmode`, `marker`, `maxbytes`, `legacyfiles`, `showreports`, `visible`, `visibleold`, `downloadcontent`, `groupmode`, `groupmodeforce`, `defaultgroupingid`, `lang`, `calendartype`, `theme`, `timecreated`, `timemodified`, `requested`, `enablecompletion`, `completionnotify`, `cacherev`, `originalcourseid`, `showactivitydates`, `showcompletionconditions`, `pdfexportfont`) VALUES
(1, 1, 1, 'Matemáticas Avanzadas', 'MAT101', 'MAT101', 'Curso de matemáticas para primer año de bachillerato', 1, 'topics', 1, 5, 1732406400, 1763942400, 0, 0, 0, 0, 0, 1, 1, NULL, 0, 0, 0, 'es', 'gregorian', '', 1732406400, 1732406400, 0, 0, 0, 0, NULL, 0, NULL, NULL),
(2, 1, 2, 'Lengua y Literatura', 'LEN201', 'LEN201', 'Curso de lengua y literatura española', 1, 'topics', 1, 5, 1732406400, 1763942400, 0, 0, 0, 0, 0, 1, 1, NULL, 0, 0, 0, 'es', 'gregorian', '', 1732406400, 1732406400, 0, 0, 0, 0, NULL, 0, NULL, NULL),
(3, 2, 3, 'Inglés Avanzado', 'ING301', 'ING301', 'Curso de inglés nivel avanzado', 1, 'topics', 1, 5, 1732406400, 1763942400, 0, 0, 0, 0, 0, 1, 1, NULL, 0, 0, 0, 'es', 'gregorian', '', 1732406400, 1732406400, 0, 0, 0, 0, NULL, 0, NULL, NULL);

-- Insertar matrículas
INSERT INTO `matriculas` (`id`, `alumno_id`, `role`, `cursos_json`, `created_at`) VALUES
(1, 1, 'estudiante', '[\"MAT101\", \"LEN201\", \"ING301\"]', '2025-10-24 19:42:26'),
(2, 2, 'estudiante', '[\"MAT101\", \"LEN201\", \"FIS202\"]', '2025-10-24 19:42:26'),
(3, 3, 'estudiante', '[\"MAT101\", \"LEN201\", \"QUI203\"]', '2025-10-24 19:42:26');

-- Insertar profesorado
INSERT INTO `profesorado` (`id`, `profesor_id`, `rol`, `cursos_json`, `updated_at`) VALUES
(1, 1, 'profesor', '[\"MAT101\", \"MAT102\"]', '2025-10-24 17:42:26'),
(2, 2, 'tutor', '[\"LEN201\", \"LEN202\"]', '2025-10-24 17:42:26'),
(3, 3, 'profesor', '[\"ING301\", \"ING302\"]', '2025-10-24 17:42:26');

-- Insertar tutorías
INSERT INTO `tutorias` (`id`, `profesor_id`, `role`, `cursos_json`, `created_at`) VALUES
(1, 1, 'tutor', '[\"1A\", \"1B\"]', '2025-10-24 17:42:26'),
(2, 2, 'tutor', '[\"2A\", \"2B\"]', '2025-10-24 17:42:26'),
(3, 3, 'tutor', '[\"3A\", \"3B\"]', '2025-10-24 17:42:26');

-- Insertar asistencias
INSERT INTO `attendance` (`id`, `module_code`, `student_id`, `present`, `date`) VALUES
(1, 'MAT101', 1, 1, '2025-10-24 08:00:00'),
(2, 'MAT101', 2, 1, '2025-10-24 08:00:00'),
(3, 'MAT101', 3, 0, '2025-10-24 08:00:00'),
(4, 'LEN201', 1, 1, '2025-10-24 10:00:00'),
(5, 'LEN201', 2, 1, '2025-10-24 10:00:00'),
(6, 'LEN201', 3, 1, '2025-10-24 10:00:00');

-- Insertar asistencias2
INSERT INTO `attendance2` (`id`, `courseid`, `username`, `date`, `time`, `present`, `comment`) VALUES
(1, 1, 'maria.garcia', '2025-10-24', '08:00', 1, 'Puntual'),
(2, 1, 'carlos.martinez', '2025-10-24', '08:00', 1, 'Puntual'),
(3, 1, 'laura.fernandez', '2025-10-24', '08:00', 0, 'Ausente justificada'),
(4, 2, 'maria.garcia', '2025-10-24', '10:00', 1, NULL),
(5, 2, 'carlos.martinez', '2025-10-24', '10:00', 1, NULL),
(6, 2, 'laura.fernandez', '2025-10-24', '10:00', 1, NULL);

-- Insertar calificaciones
INSERT INTO `calificaciones` (`id`, `alumno_id`, `asignatura_code`, `calificacion`, `period`) VALUES
(1, 1, 'MAT101', '8.5', 'Q1-2025'),
(2, 1, 'LEN201', '9.0', 'Q1-2025'),
(3, 2, 'MAT101', '7.2', 'Q1-2025'),
(4, 2, 'LEN201', '8.8', 'Q1-2025'),
(5, 3, 'MAT101', '6.5', 'Q1-2025'),
(6, 3, 'LEN201', '9.5', 'Q1-2025');

-- Insertar calificaciones2
INSERT INTO `calificaciones2` (`id`, `courseid`, `username`, `period`, `calificacion`) VALUES
(1, 1, 'maria.garcia', 'Q1-2025', 85),
(2, 2, 'maria.garcia', 'Q1-2025', 90),
(3, 1, 'carlos.martinez', 'Q1-2025', 72),
(4, 2, 'carlos.martinez', 'Q1-2025', 88),
(5, 1, 'laura.fernandez', 'Q1-2025', 65),
(6, 2, 'laura.fernandez', 'Q1-2025', 95);

-- Insertar documentos
INSERT INTO `documentos` (`id`, `title`, `content`, `owner_id`, `created_at`, `updated_at`) VALUES
(1, 'Planificación Anual Matemáticas', 'Contenido del plan de estudios de matemáticas para el curso 2024-2025...', 1, '2025-10-24 17:42:26', '2025-10-24 17:42:26'),
(2, 'Reglamento Interno', 'Normas y procedimientos del centro educativo...', 2, '2025-10-24 17:42:26', '2025-10-24 17:42:26'),
(3, 'Actividades Extraescolares', 'Programación de actividades complementarias...', 1, '2025-10-24 17:42:26', '2025-10-24 17:42:26');

-- Añadir restricciones de clave foránea
ALTER TABLE `calificaciones`
  ADD CONSTRAINT `calificaciones_ibfk_1` FOREIGN KEY (`alumno_id`) REFERENCES `alumnos` (`Identificador`);

ALTER TABLE `tutorias`
  ADD CONSTRAINT `tutorias_ibfk_1` FOREIGN KEY (`profesor_id`) REFERENCES `profesores` (`id`);

-- Mostrar mensaje de confirmación
SELECT 'Base de datos sisi creada exitosamente con datos de ejemplo' AS 'Estado';