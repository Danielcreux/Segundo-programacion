    -- =============================================
    -- ESQUEMA DE BASE DE DATOS TIENDA ONLINE
    -- =============================================

    -- Eliminar tablas si existen (en orden inverso de dependencias)
    DROP TABLE IF EXISTS articulos_pedido;
    DROP TABLE IF EXISTS pedidos;
    DROP TABLE IF EXISTS articulos_carrito;
    DROP TABLE IF EXISTS imagenes_producto;
    DROP TABLE IF EXISTS resenas_producto;
    DROP TABLE IF EXISTS productos;
    DROP TABLE IF EXISTS categorias;
    DROP TABLE IF EXISTS marcas;
    DROP TABLE IF EXISTS metodos_pago;
    DROP TABLE IF EXISTS metodos_envio;
    DROP TABLE IF EXISTS direcciones;
    DROP TABLE IF EXISTS clientes;
    DROP TABLE IF EXISTS paises;
    DROP TABLE IF EXISTS ciudades;
    DROP TABLE IF EXISTS estados_pedido;
    DROP TABLE IF EXISTS estados_pago;

    -- =============================================
    -- TABLAS DE BÚSQUEDA/REFERENCIA
    -- =============================================

    -- Tabla de países
    CREATE TABLE paises (
        id_pais INT PRIMARY KEY AUTO_INCREMENT,
        nombre_pais VARCHAR(100) NOT NULL UNIQUE,
        codigo_pais CHAR(2) NOT NULL UNIQUE,
        prefijo_telefono VARCHAR(10)
    );

    -- Tabla de ciudades
    CREATE TABLE ciudades (
        id_ciudad INT PRIMARY KEY AUTO_INCREMENT,
        nombre_ciudad VARCHAR(100) NOT NULL,
        id_pais INT NOT NULL,
        codigo_postal VARCHAR(20),
        FOREIGN KEY (id_pais) REFERENCES paises(id_pais),
        UNIQUE KEY ciudad_pais_unico (nombre_ciudad, id_pais)
    );

    -- Estados de pedido
    CREATE TABLE estados_pedido (
        id_estado INT PRIMARY KEY AUTO_INCREMENT,
        nombre_estado VARCHAR(50) NOT NULL UNIQUE,
        descripcion_estado VARCHAR(255)
    );

    -- Estados de pago
    CREATE TABLE estados_pago (
        id_estado_pago INT PRIMARY KEY AUTO_INCREMENT,
        nombre_estado VARCHAR(50) NOT NULL UNIQUE
    );

    -- Métodos de envío
    CREATE TABLE metodos_envio (
        id_metodo_envio INT PRIMARY KEY AUTO_INCREMENT,
        nombre_metodo VARCHAR(100) NOT NULL UNIQUE,
        coste_base DECIMAL(10, 2) NOT NULL,
        dias_estimados INT,
        descripcion TEXT
    );

    -- Métodos de pago
    CREATE TABLE metodos_pago (
        id_metodo_pago INT PRIMARY KEY AUTO_INCREMENT,
        nombre_metodo VARCHAR(50) NOT NULL UNIQUE,
        esta_activo BOOLEAN DEFAULT TRUE
    );

    -- Tabla de marcas
    CREATE TABLE marcas (
        id_marca INT PRIMARY KEY AUTO_INCREMENT,
        nombre_marca VARCHAR(100) NOT NULL UNIQUE,
        descripcion_marca TEXT,
        url_sitio_web VARCHAR(255)
    );

    -- Tabla de categorías
    CREATE TABLE categorias (
        id_categoria INT PRIMARY KEY AUTO_INCREMENT,
        nombre_categoria VARCHAR(100) NOT NULL UNIQUE,
        id_categoria_padre INT,
        descripcion_categoria TEXT,
        FOREIGN KEY (id_categoria_padre) REFERENCES categorias(id_categoria)
    );

    -- =============================================
    -- TABLAS RELACIONADAS CON CLIENTES
    -- =============================================

    -- Tabla de clientes
    CREATE TABLE clientes (
        id_cliente INT PRIMARY KEY AUTO_INCREMENT,
        email VARCHAR(255) NOT NULL UNIQUE,
        hash_contrasena VARCHAR(255) NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        apellido VARCHAR(100) NOT NULL,
        telefono VARCHAR(20),
        fecha_nacimiento DATE,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ultimo_acceso TIMESTAMP NULL DEFAULT NULL,
        esta_activo BOOLEAN DEFAULT TRUE
    );

    -- Tabla de direcciones
    CREATE TABLE direcciones (
        id_direccion INT PRIMARY KEY AUTO_INCREMENT,
        id_cliente INT NOT NULL,
        tipo_direccion ENUM('facturacion', 'envio', 'ambos') NOT NULL,
        direccion_calle VARCHAR(255) NOT NULL,
        apartamento VARCHAR(50),
        id_ciudad INT NOT NULL,
        codigo_postal VARCHAR(20),
        es_predeterminada BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE,
        FOREIGN KEY (id_ciudad) REFERENCES ciudades(id_ciudad)
    );

    -- =============================================
    -- TABLAS RELACIONADAS CON PRODUCTOS
    -- =============================================

    -- Tabla de productos
    CREATE TABLE productos (
        id_producto INT PRIMARY KEY AUTO_INCREMENT,
        nombre_producto VARCHAR(255) NOT NULL,
        sku VARCHAR(100) NOT NULL UNIQUE,
        id_categoria INT NOT NULL,
        id_marca INT,
        descripcion TEXT,
        precio DECIMAL(10, 2) NOT NULL,
        porcentaje_descuento DECIMAL(5, 2) DEFAULT 0,
        cantidad_stock INT NOT NULL DEFAULT 0,
        peso_kg DECIMAL(8, 2),
        esta_activo BOOLEAN DEFAULT TRUE,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
        FOREIGN KEY (id_marca) REFERENCES marcas(id_marca)
    );

    -- Tabla de imágenes de productos
    CREATE TABLE imagenes_producto (
        id_imagen INT PRIMARY KEY AUTO_INCREMENT,
        id_producto INT NOT NULL,
        url_imagen VARCHAR(500) NOT NULL,
        es_principal BOOLEAN DEFAULT FALSE,
        orden_visualizacion INT DEFAULT 0,
        FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE
    );

    -- Tabla de reseñas de productos
    CREATE TABLE resenas_producto (
        id_resena INT PRIMARY KEY AUTO_INCREMENT,
        id_producto INT NOT NULL,
        id_cliente INT NOT NULL,
        valoracion INT NOT NULL CHECK (valoracion BETWEEN 1 AND 5),
        titulo_resena VARCHAR(255),
        texto_resena TEXT,
        fecha_resena TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        es_compra_verificada BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE
    );

    -- =============================================
    -- TABLAS DE CARRITO DE COMPRAS
    -- =============================================

    -- Tabla de artículos del carrito
    CREATE TABLE articulos_carrito (
        id_articulo_carrito INT PRIMARY KEY AUTO_INCREMENT,
        id_cliente INT NOT NULL,
        id_producto INT NOT NULL,
        cantidad INT NOT NULL DEFAULT 1,
        fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE,
        FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
        UNIQUE KEY cliente_producto_unico (id_cliente, id_producto)
    );

    -- =============================================
    -- TABLAS RELACIONADAS CON PEDIDOS
    -- =============================================

    -- Tabla de pedidos
    CREATE TABLE pedidos (
        id_pedido INT PRIMARY KEY AUTO_INCREMENT,
        id_cliente INT NOT NULL,
        numero_pedido VARCHAR(50) NOT NULL UNIQUE,
        fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        id_estado INT NOT NULL,
        id_estado_pago INT NOT NULL,
        id_metodo_pago INT NOT NULL,
        id_metodo_envio INT NOT NULL,
        id_direccion_envio INT NOT NULL,
        id_direccion_facturacion INT NOT NULL,
        subtotal DECIMAL(10, 2) NOT NULL,
        monto_impuestos DECIMAL(10, 2) NOT NULL,
        coste_envio DECIMAL(10, 2) NOT NULL,
        monto_descuento DECIMAL(10, 2) DEFAULT 0,
        monto_total DECIMAL(10, 2) NOT NULL,
        notas TEXT,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_estado) REFERENCES estados_pedido(id_estado),
        FOREIGN KEY (id_estado_pago) REFERENCES estados_pago(id_estado_pago),
        FOREIGN KEY (id_metodo_pago) REFERENCES metodos_pago(id_metodo_pago),
        FOREIGN KEY (id_metodo_envio) REFERENCES metodos_envio(id_metodo_envio),
        FOREIGN KEY (id_direccion_envio) REFERENCES direcciones(id_direccion),
        FOREIGN KEY (id_direccion_facturacion) REFERENCES direcciones(id_direccion)
    );

    -- Tabla de artículos del pedido
    CREATE TABLE articulos_pedido (
        id_articulo_pedido INT PRIMARY KEY AUTO_INCREMENT,
        id_pedido INT NOT NULL,
        id_producto INT NOT NULL,
        cantidad INT NOT NULL,
        precio_unitario DECIMAL(10, 2) NOT NULL,
        monto_descuento DECIMAL(10, 2) DEFAULT 0,
        precio_total DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
        FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
    );

    -- =============================================
    -- INSERTAR DATOS DE EJEMPLO
    -- =============================================

    -- Insertar Países
    INSERT INTO paises (nombre_pais, codigo_pais, prefijo_telefono) VALUES
    ('España', 'ES', '+34'),
    ('Estados Unidos', 'US', '+1'),
    ('Reino Unido', 'UK', '+44'),
    ('Alemania', 'DE', '+49'),
    ('Francia', 'FR', '+33');

    -- Insertar Ciudades
    INSERT INTO ciudades (nombre_ciudad, id_pais, codigo_postal) VALUES
    ('Madrid', 1, '28001'),
    ('Barcelona', 1, '08001'),
    ('Nueva York', 2, '10001'),
    ('Los Ángeles', 2, '90001'),
    ('Londres', 3, 'SW1A'),
    ('Berlín', 4, '10115'),
    ('París', 5, '75001');

    -- Insertar Estados de Pedido
    INSERT INTO estados_pedido (nombre_estado, descripcion_estado) VALUES
    ('Pendiente', 'El pedido ha sido realizado pero aún no procesado'),
    ('En Proceso', 'El pedido se está preparando'),
    ('Enviado', 'El pedido ha sido enviado'),
    ('Entregado', 'El pedido ha sido entregado'),
    ('Cancelado', 'El pedido ha sido cancelado'),
    ('Reembolsado', 'El pedido ha sido reembolsado');

    -- Insertar Estados de Pago
    INSERT INTO estados_pago (nombre_estado) VALUES
    ('Pendiente'),
    ('Completado'),
    ('Fallido'),
    ('Reembolsado');

    -- Insertar Métodos de Envío
    INSERT INTO metodos_envio (nombre_metodo, coste_base, dias_estimados, descripcion) VALUES
    ('Envío Estándar', 5.99, 7, 'Entrega regular en 5-7 días laborables'),
    ('Envío Exprés', 14.99, 3, 'Entrega rápida en 2-3 días laborables'),
    ('Envío Urgente', 29.99, 1, 'Entrega al día siguiente'),
    ('Envío Gratuito', 0.00, 10, 'Entrega estándar gratuita para pedidos superiores a 50€');

    -- Insertar Métodos de Pago
    INSERT INTO metodos_pago (nombre_metodo, esta_activo) VALUES
    ('Tarjeta de Crédito', TRUE),
    ('Tarjeta de Débito', TRUE),
    ('PayPal', TRUE),
    ('Apple Pay', TRUE),
    ('Google Pay', TRUE),
    ('Transferencia Bancaria', TRUE);

    -- Insertar Marcas
    INSERT INTO marcas (nombre_marca, descripcion_marca, url_sitio_web) VALUES
    ('TechMaster', 'Fabricante líder de electrónica', 'https://techmaster.example.com'),
    ('StyleWear', 'Marca de moda y ropa', 'https://stylewear.example.com'),
    ('HomeComfort', 'Productos para el hogar', 'https://homecomfort.example.com'),
    ('SportPro', 'Equipamiento deportivo y fitness', 'https://sportpro.example.com'),
    ('BeautyGlow', 'Belleza y cosmética', 'https://beautyglow.example.com');

    -- Insertar Categorías
    INSERT INTO categorias (nombre_categoria, id_categoria_padre, descripcion_categoria) VALUES
    ('Electrónica', NULL, 'Dispositivos electrónicos y accesorios'),
    ('Ropa', NULL, 'Ropa y artículos de moda'),
    ('Hogar y Jardín', NULL, 'Mejoras para el hogar y suministros de jardín'),
    ('Deportes y Aire Libre', NULL, 'Equipamiento deportivo y artículos de exterior'),
    ('Belleza y Salud', NULL, 'Productos de belleza y artículos de salud'),
    ('Smartphones', 1, 'Teléfonos móviles y accesorios'),
    ('Portátiles', 1, 'Ordenadores portátiles'),
    ('Ropa de Hombre', 2, 'Ropa para hombres'),
    ('Ropa de Mujer', 2, 'Ropa para mujeres'),
    ('Muebles', 3, 'Muebles para el hogar');

    -- Insertar Clientes
    INSERT INTO clientes (email, hash_contrasena, nombre, apellido, telefono, fecha_nacimiento) VALUES
    ('juan.perez@email.com', 'hash123abc', 'Juan', 'Pérez', '+34600123456', '1985-03-15'),
    ('maria.garcia@email.com', 'hash456def', 'María', 'García', '+34600234567', '1990-07-22'),
    ('james.smith@email.com', 'hash789ghi', 'James', 'Smith', '+1555123456', '1988-11-30'),
    ('sophie.martin@email.com', 'hash012jkl', 'Sophie', 'Martin', '+33612345678', '1992-05-18'),
    ('hans.mueller@email.com', 'hash345mno', 'Hans', 'Müller', '+49151234567', '1987-09-25');

    -- Insertar Direcciones
    INSERT INTO direcciones (id_cliente, tipo_direccion, direccion_calle, apartamento, id_ciudad, codigo_postal, es_predeterminada) VALUES
    (1, 'ambos', 'Calle Gran Vía 123', '3A', 1, '28013', TRUE),
    (2, 'envio', 'Paseo de Gracia 456', NULL, 2, '08007', TRUE),
    (2, 'facturacion', 'Rambla Catalunya 789', '2B', 2, '08008', FALSE),
    (3, 'ambos', '5th Avenue 789', 'Apt 12C', 3, '10022', TRUE),
    (4, 'ambos', 'Champs-Élysées 101', NULL, 7, '75008', TRUE),
    (5, 'ambos', 'Unter den Linden 55', NULL, 6, '10117', TRUE);

    -- Insertar Productos
    INSERT INTO productos (nombre_producto, sku, id_categoria, id_marca, descripcion, precio, porcentaje_descuento, cantidad_stock, peso_kg) VALUES
    ('Smartphone TechMaster X1', 'TM-SP-X1-001', 6, 1, 'Último smartphone con 128GB de almacenamiento y conectividad 5G', 699.99, 10, 50, 0.18),
    ('Portátil TechMaster Pro 15', 'TM-LP-PRO15-001', 7, 1, 'Portátil de 15 pulgadas con procesador Intel i7 y 16GB RAM', 1299.99, 15, 25, 2.1),
    ('Camiseta de Algodón para Hombre StyleWear', 'SW-TS-MCT-BLU-M', 8, 2, 'Cómoda camiseta de algodón en azul - Talla M', 29.99, 0, 100, 0.2),
    ('Vestido de Verano para Mujer StyleWear', 'SW-DR-WSD-RED-M', 9, 2, 'Elegante vestido de verano en rojo - Talla M', 79.99, 20, 45, 0.3),
    ('Silla de Oficina HomeComfort', 'HC-CH-OFF-BLK', 10, 3, 'Silla de oficina ergonómica con soporte lumbar', 249.99, 0, 30, 15.5),
    ('Zapatillas para Correr SportPro', 'SP-SH-RUN-BLK-42', 4, 4, 'Zapatillas profesionales para correr - Talla 42', 119.99, 25, 60, 0.8),
    ('Crema Facial BeautyGlow', 'BG-FC-HYD-50ML', 5, 5, 'Crema facial hidratante 50ml', 49.99, 0, 150, 0.1),
    ('Auriculares Inalámbricos TechMaster', 'TM-EB-WRL-001', 6, 1, 'Auriculares inalámbricos con cancelación de ruido y estuche de carga', 149.99, 5, 80, 0.05);

    -- Insertar Imágenes de Productos
    INSERT INTO imagenes_producto (id_producto, url_imagen, es_principal, orden_visualizacion) VALUES
    (1, 'https://cdn.example.com/productos/smartphone-x1-frontal.jpg', TRUE, 1),
    (1, 'https://cdn.example.com/productos/smartphone-x1-trasera.jpg', FALSE, 2),
    (2, 'https://cdn.example.com/productos/portatil-pro15-principal.jpg', TRUE, 1),
    (3, 'https://cdn.example.com/productos/camiseta-azul-frontal.jpg', TRUE, 1),
    (4, 'https://cdn.example.com/productos/vestido-rojo-frontal.jpg', TRUE, 1),
    (5, 'https://cdn.example.com/productos/silla-oficina-principal.jpg', TRUE, 1),
    (6, 'https://cdn.example.com/productos/zapatillas-correr-principal.jpg', TRUE, 1),
    (7, 'https://cdn.example.com/productos/crema-facial-principal.jpg', TRUE, 1),
    (8, 'https://cdn.example.com/productos/auriculares-principal.jpg', TRUE, 1);

    -- Insertar Reseñas de Productos
    INSERT INTO resenas_producto (id_producto, id_cliente, valoracion, titulo_resena, texto_resena, es_compra_verificada) VALUES
    (1, 1, 5, '¡Teléfono excelente!', 'El mejor smartphone que he tenido. Rápido, confiable y con una gran calidad de cámara.', TRUE),
    (1, 3, 4, 'Bueno pero caro', 'Muy buen teléfono en general, pero un poco caro. La batería podría durar más.', TRUE),
    (2, 2, 5, 'Perfecto para trabajar', 'Este portátil maneja todas mis tareas de trabajo sin esfuerzo. ¡Muy recomendable!', TRUE),
    (3, 4, 5, 'Muy cómoda', 'Camiseta de gran calidad, se ajusta perfectamente y la tela es suave.', TRUE),
    (6, 5, 4, 'Excelentes zapatillas para correr', 'Cómodas y ligeras. Perfectas para mis carreras diarias.', TRUE);

    -- Insertar Artículos del Carrito
    INSERT INTO articulos_carrito (id_cliente, id_producto, cantidad) VALUES
    (1, 8, 1),
    (1, 7, 2),
    (3, 3, 3),
    (5, 6, 1);

    -- Insertar Pedidos
    INSERT INTO pedidos (id_cliente, numero_pedido, id_estado, id_estado_pago, id_metodo_pago, id_metodo_envio, 
                       id_direccion_envio, id_direccion_facturacion, subtotal, monto_impuestos, coste_envio, monto_descuento, monto_total) VALUES
    (1, 'PED-2024-001', 4, 2, 1, 2, 1, 1, 629.99, 132.30, 14.99, 70.00, 707.28),
    (2, 'PED-2024-002', 3, 2, 3, 1, 2, 3, 63.99, 13.44, 5.99, 16.00, 67.42),
    (3, 'PED-2024-003', 2, 2, 2, 3, 4, 4, 89.97, 18.89, 29.99, 0, 138.85),
    (4, 'PED-2024-004', 4, 2, 4, 1, 5, 5, 1299.99, 273.00, 0.00, 194.99, 1378.00),
    (5, 'PED-2024-005', 1, 1, 1, 1, 6, 6, 89.99, 18.90, 5.99, 30.00, 84.88);

    -- Insertar Artículos del Pedido
    INSERT INTO articulos_pedido (id_pedido, id_producto, cantidad, precio_unitario, monto_descuento, precio_total) VALUES
    (1, 1, 1, 699.99, 70.00, 629.99),
    (2, 4, 1, 79.99, 16.00, 63.99),
    (3, 3, 3, 29.99, 0, 89.97),
    (4, 2, 1, 1299.99, 194.99, 1105.00),
    (5, 6, 1, 119.99, 30.00, 89.99);

    -- =============================================
    -- CONSULTAS ÚTILES
    -- =============================================

    -- Mostrar todos los productos con sus categorías y marcas
    SELECT 
        p.nombre_producto,
        p.sku,
        c.nombre_categoria,
        m.nombre_marca,
        p.precio,
        p.cantidad_stock
    FROM productos p
    LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
    LEFT JOIN marcas m ON p.id_marca = m.id_marca;

    -- Mostrar pedidos de clientes con detalles
    SELECT 
        pe.numero_pedido,
        CONCAT(cl.nombre, ' ', cl.apellido) AS nombre_cliente,
        pe.fecha_pedido,
        ep.nombre_estado,
        pe.monto_total
    FROM pedidos pe
    JOIN clientes cl ON pe.id_cliente = cl.id_cliente
    JOIN estados_pedido ep ON pe.id_estado = ep.id_estado
    ORDER BY pe.fecha_pedido DESC;
