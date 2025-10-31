-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: d368.dinaserver.com:3306
-- Tiempo de generación: 24-10-2025 a las 19:42:26
-- Versión del servidor: 10.11.14-MariaDB-deb11-log
-- Versión de PHP: 8.2.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `sisi_sis`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alumnos`
--

CREATE TABLE `alumnos` (
  `Identificador` int(11) NOT NULL,
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
  `Nombre del padre` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `attendance`
--

CREATE TABLE `attendance` (
  `id` int(11) NOT NULL,
  `module_code` varchar(255) NOT NULL,
  `student_id` int(11) NOT NULL,
  `present` tinyint(1) NOT NULL,
  `date` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `attendance2`
--

CREATE TABLE `attendance2` (
  `id` int(10) UNSIGNED NOT NULL,
  `courseid` int(10) UNSIGNED DEFAULT NULL,
  `username` varchar(191) NOT NULL,
  `date` date NOT NULL,
  `time` char(5) NOT NULL,
  `present` tinyint(1) NOT NULL DEFAULT 0,
  `comment` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `calificaciones`
--

CREATE TABLE `calificaciones` (
  `id` int(11) NOT NULL,
  `alumno_id` int(11) NOT NULL,
  `asignatura_code` varchar(255) NOT NULL,
  `calificacion` varchar(10) DEFAULT NULL,
  `period` varchar(20) NOT NULL DEFAULT 'DEFAULT-PERIOD'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `calificaciones2`
--

CREATE TABLE `calificaciones2` (
  `id` int(10) UNSIGNED NOT NULL,
  `courseid` int(10) UNSIGNED NOT NULL,
  `username` varchar(191) NOT NULL,
  `period` varchar(64) NOT NULL,
  `calificacion` tinyint(3) UNSIGNED DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `documentos`
--

CREATE TABLE `documentos` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text DEFAULT NULL,
  `owner_id` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `matriculas`
--

CREATE TABLE `matriculas` (
  `id` int(11) NOT NULL,
  `alumno_id` int(11) NOT NULL,
  `role` enum('estudiante','profesor') NOT NULL,
  `cursos_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`cursos_json`)),
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mdl_course`
--

CREATE TABLE `mdl_course` (
  `id` bigint(10) NOT NULL,
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
  `pdfexportfont` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci COMMENT='Central course table' ROW_FORMAT=COMPRESSED;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `profesorado`
--

CREATE TABLE `profesorado` (
  `id` int(11) NOT NULL,
  `profesor_id` int(11) NOT NULL,
  `rol` varchar(50) NOT NULL DEFAULT 'profesor',
  `cursos_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`cursos_json`)),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `profesores`
--

CREATE TABLE `profesores` (
  `id` int(11) NOT NULL,
  `DNI` varchar(200) NOT NULL,
  `Nombre` varchar(100) DEFAULT NULL,
  `Apellido1` varchar(100) DEFAULT NULL,
  `Apellido2` varchar(255) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tutorias`
--

CREATE TABLE `tutorias` (
  `id` int(11) NOT NULL,
  `profesor_id` int(11) NOT NULL,
  `role` varchar(50) NOT NULL,
  `cursos_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`cursos_json`)),
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `Identificador` int(11) NOT NULL,
  `usuario` varchar(20) NOT NULL,
  `contrasena` varchar(20) NOT NULL,
  `nombre` varchar(20) NOT NULL,
  `apellido1` varchar(20) NOT NULL,
  `apellido2` varchar(20) NOT NULL,
  `perfil` enum('direccion','docentes','secretaria','') NOT NULL,
  `email` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vista_duplicados`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `vista_duplicados` (
`id_1` int(10) unsigned
,`courseid` int(10) unsigned
,`username` varchar(191)
,`date` date
,`time_1` char(5)
,`id_2` int(10) unsigned
,`time_2` char(5)
,`diff_min` bigint(21)
);

-- --------------------------------------------------------

--
-- Estructura para la vista `vista_duplicados`
--
DROP TABLE IF EXISTS `vista_duplicados`;

CREATE ALGORITHM=UNDEFINED DEFINER=`sisi_admin`@`%` SQL SECURITY DEFINER VIEW `vista_duplicados`  AS SELECT `a1`.`id` AS `id_1`, `a1`.`courseid` AS `courseid`, `a1`.`username` AS `username`, `a1`.`date` AS `date`, `a1`.`time` AS `time_1`, `a2`.`id` AS `id_2`, `a2`.`time` AS `time_2`, abs(timestampdiff(MINUTE,str_to_date(concat(`a1`.`date`,' ',`a1`.`time`),'%Y-%m-%d %H:%i'),str_to_date(concat(`a2`.`date`,' ',`a2`.`time`),'%Y-%m-%d %H:%i'))) AS `diff_min` FROM (`attendance2` `a1` join `attendance2` `a2` on(`a1`.`courseid` = `a2`.`courseid` and `a1`.`username` = `a2`.`username` and `a1`.`date` = `a2`.`date` and `a1`.`id` < `a2`.`id`)) WHERE abs(timestampdiff(MINUTE,str_to_date(concat(`a1`.`date`,' ',`a1`.`time`),'%Y-%m-%d %H:%i'),str_to_date(concat(`a2`.`date`,' ',`a2`.`time`),'%Y-%m-%d %H:%i'))) < 5 ORDER BY `a1`.`courseid` ASC, `a1`.`username` ASC, `a1`.`date` ASC, `a1`.`time` ASC, `a2`.`time` ASC ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `alumnos`
--
ALTER TABLE `alumnos`
  ADD PRIMARY KEY (`Identificador`);

--
-- Indices de la tabla `attendance`
--
ALTER TABLE `attendance`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `attendance2`
--
ALTER TABLE `attendance2`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_date` (`username`,`date`),
  ADD KEY `idx_att2_course_user` (`courseid`,`username`);

--
-- Indices de la tabla `calificaciones`
--
ALTER TABLE `calificaciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `alumno_id` (`alumno_id`);

--
-- Indices de la tabla `calificaciones2`
--
ALTER TABLE `calificaciones2`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_course_user_period` (`courseid`,`username`,`period`),
  ADD KEY `idx_course_user` (`courseid`,`username`);

--
-- Indices de la tabla `documentos`
--
ALTER TABLE `documentos`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `matriculas`
--
ALTER TABLE `matriculas`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `mdl_course`
--
ALTER TABLE `mdl_course`
  ADD PRIMARY KEY (`id`),
  ADD KEY `mdl_cour_cat_ix` (`category`),
  ADD KEY `mdl_cour_idn_ix` (`idnumber`),
  ADD KEY `mdl_cour_sho_ix` (`shortname`),
  ADD KEY `mdl_cour_sor_ix` (`sortorder`),
  ADD KEY `mdl_cour_ori_ix` (`originalcourseid`);

--
-- Indices de la tabla `profesorado`
--
ALTER TABLE `profesorado`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_profesor` (`profesor_id`);

--
-- Indices de la tabla `profesores`
--
ALTER TABLE `profesores`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `tutorias`
--
ALTER TABLE `tutorias`
  ADD PRIMARY KEY (`id`),
  ADD KEY `profesor_id` (`profesor_id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`Identificador`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `alumnos`
--
ALTER TABLE `alumnos`
  MODIFY `Identificador` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `attendance`
--
ALTER TABLE `attendance`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `attendance2`
--
ALTER TABLE `attendance2`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `calificaciones`
--
ALTER TABLE `calificaciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `calificaciones2`
--
ALTER TABLE `calificaciones2`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `documentos`
--
ALTER TABLE `documentos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `matriculas`
--
ALTER TABLE `matriculas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `mdl_course`
--
ALTER TABLE `mdl_course`
  MODIFY `id` bigint(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `profesorado`
--
ALTER TABLE `profesorado`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `profesores`
--
ALTER TABLE `profesores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tutorias`
--
ALTER TABLE `tutorias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `Identificador` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `calificaciones`
--
ALTER TABLE `calificaciones`
  ADD CONSTRAINT `calificaciones_ibfk_1` FOREIGN KEY (`alumno_id`) REFERENCES `alumnos` (`Identificador`);

--
-- Filtros para la tabla `tutorias`
--
ALTER TABLE `tutorias`
  ADD CONSTRAINT `tutorias_ibfk_1` FOREIGN KEY (`profesor_id`) REFERENCES `profesores` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;