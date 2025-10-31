-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 24-10-2025 a las 16:11:38
-- Versión del servidor: 8.0.43-0ubuntu0.24.04.1
-- Versión de PHP: 8.3.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `crimson`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `aplicaciones`
--

CREATE TABLE `aplicaciones` (
  `Identificador` int NOT NULL,
  `nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `icono` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `ruta` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `activa` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clavesapi`
--

CREATE TABLE `clavesapi` (
  `Identificador` int NOT NULL,
  `suscriptor` varchar(255) NOT NULL,
  `clave` varchar(255) NOT NULL,
  `ipservidor` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `Identificador` int NOT NULL,
  `nombre` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `apellidos` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `direccion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `poblacion` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `cp` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `pais` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `texto` text CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci COMMENT='En esta tabla guardamos los clientes de la aplicación';

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `clientes_resumido`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `clientes_resumido` (
`apellidos` varchar(255)
,`Identificador` int
,`nombre` varchar(255)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `departamentos`
--

CREATE TABLE `departamentos` (
  `Identificador` int NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `departamentosaplicaciones`
--

CREATE TABLE `departamentosaplicaciones` (
  `Identificador` int NOT NULL,
  `departamentos_nombre` int NOT NULL,
  `aplicaciones_nombre` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `lineaspedido`
--

CREATE TABLE `lineaspedido` (
  `Identificador` int NOT NULL,
  `pedidos_fecha` int NOT NULL,
  `productos_nombre` int NOT NULL,
  `cantidad` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos`
--

CREATE TABLE `pedidos` (
  `Identificador` int NOT NULL,
  `fecha` date DEFAULT NULL,
  `clientes_nombre` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci COMMENT='En esta tabla guardamos los pedidos que se gestionan en la aplicacion';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `Identificador` int NOT NULL,
  `nombre` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `precio` decimal(10,2) DEFAULT NULL,
  `fotografia` longblob
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registros`
--

CREATE TABLE `registros` (
  `Identificador` int NOT NULL,
  `epoch` int NOT NULL,
  `ip` varchar(255) NOT NULL,
  `navegador` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  `comentarios` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `seleccion_clientes`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `seleccion_clientes` (
`direccion` text
,`email` varchar(255)
,`nombrecompleto` varchar(511)
,`poblacion` varchar(255)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tablasaplicaciones`
--

CREATE TABLE `tablasaplicaciones` (
  `Identificador` int NOT NULL,
  `aplicaciones_nombre` int NOT NULL,
  `tabla` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `Identificador` int NOT NULL,
  `usuario` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `contrasena` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `apellidos` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `departamentos_nombre` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura para la vista `clientes_resumido`
--
DROP TABLE IF EXISTS `clientes_resumido`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `clientes_resumido`  AS SELECT `clientes`.`Identificador` AS `Identificador`, `clientes`.`nombre` AS `nombre`, `clientes`.`apellidos` AS `apellidos` FROM `clientes` ;

-- --------------------------------------------------------

--
-- Estructura para la vista `seleccion_clientes`
--
DROP TABLE IF EXISTS `seleccion_clientes`;

CREATE ALGORITHM=UNDEFINED DEFINER=`crimson`@`localhost` SQL SECURITY DEFINER VIEW `seleccion_clientes`  AS SELECT concat(`clientes`.`nombre`,' ',`clientes`.`apellidos`) AS `nombrecompleto`, `clientes`.`email` AS `email`, `clientes`.`direccion` AS `direccion`, `clientes`.`poblacion` AS `poblacion` FROM `clientes` WHERE (`clientes`.`nombre` like '%ju%') ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `aplicaciones`
--
ALTER TABLE `aplicaciones`
  ADD PRIMARY KEY (`Identificador`);

--
-- Indices de la tabla `clavesapi`
--
ALTER TABLE `clavesapi`
  ADD PRIMARY KEY (`Identificador`);

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`Identificador`);

--
-- Indices de la tabla `departamentos`
--
ALTER TABLE `departamentos`
  ADD PRIMARY KEY (`Identificador`);

--
-- Indices de la tabla `departamentosaplicaciones`
--
ALTER TABLE `departamentosaplicaciones`
  ADD PRIMARY KEY (`Identificador`),
  ADD KEY `departamentosaplicaciones_departamentos` (`departamentos_nombre`),
  ADD KEY `departamentosaplicaciones_aplicaciones` (`aplicaciones_nombre`);

--
-- Indices de la tabla `lineaspedido`
--
ALTER TABLE `lineaspedido`
  ADD PRIMARY KEY (`Identificador`),
  ADD KEY `lineaspedidoapedido` (`pedidos_fecha`),
  ADD KEY `lineaspedidoaproducto` (`productos_nombre`);

--
-- Indices de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD PRIMARY KEY (`Identificador`),
  ADD KEY `pedidosaclientes` (`clientes_nombre`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`Identificador`);

--
-- Indices de la tabla `registros`
--
ALTER TABLE `registros`
  ADD PRIMARY KEY (`Identificador`);

--
-- Indices de la tabla `tablasaplicaciones`
--
ALTER TABLE `tablasaplicaciones`
  ADD PRIMARY KEY (`Identificador`),
  ADD KEY `tablasaplicacionesatablas` (`aplicaciones_nombre`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`Identificador`),
  ADD KEY `usuariosdepartamentos` (`departamentos_nombre`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `aplicaciones`
--
ALTER TABLE `aplicaciones`
  MODIFY `Identificador` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `clavesapi`
--
ALTER TABLE `clavesapi`
  MODIFY `Identificador` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `clientes`
--
ALTER TABLE `clientes`
  MODIFY `Identificador` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `departamentos`
--
ALTER TABLE `departamentos`
  MODIFY `Identificador` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `departamentosaplicaciones`
--
ALTER TABLE `departamentosaplicaciones`
  MODIFY `Identificador` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `lineaspedido`
--
ALTER TABLE `lineaspedido`
  MODIFY `Identificador` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  MODIFY `Identificador` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `Identificador` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `registros`
--
ALTER TABLE `registros`
  MODIFY `Identificador` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tablasaplicaciones`
--
ALTER TABLE `tablasaplicaciones`
  MODIFY `Identificador` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `Identificador` int NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `departamentosaplicaciones`
--
ALTER TABLE `departamentosaplicaciones`
  ADD CONSTRAINT `departamentosaplicaciones_aplicaciones` FOREIGN KEY (`aplicaciones_nombre`) REFERENCES `aplicaciones` (`Identificador`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  ADD CONSTRAINT `departamentosaplicaciones_departamentos` FOREIGN KEY (`departamentos_nombre`) REFERENCES `departamentos` (`Identificador`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Filtros para la tabla `lineaspedido`
--
ALTER TABLE `lineaspedido`
  ADD CONSTRAINT `lineaspedidoapedido` FOREIGN KEY (`pedidos_fecha`) REFERENCES `pedidos` (`Identificador`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  ADD CONSTRAINT `lineaspedidoaproducto` FOREIGN KEY (`productos_nombre`) REFERENCES `productos` (`Identificador`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Filtros para la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD CONSTRAINT `pedidosaclientes` FOREIGN KEY (`clientes_nombre`) REFERENCES `clientes` (`Identificador`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Filtros para la tabla `tablasaplicaciones`
--
ALTER TABLE `tablasaplicaciones`
  ADD CONSTRAINT `tablasaplicacionesatablas` FOREIGN KEY (`aplicaciones_nombre`) REFERENCES `aplicaciones` (`Identificador`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Filtros para la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD CONSTRAINT `usuariosdepartamentos` FOREIGN KEY (`departamentos_nombre`) REFERENCES `departamentos` (`Identificador`) ON DELETE RESTRICT ON UPDATE RESTRICT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;