-- 1. Crear la base de datos
CREATE DATABASE IF NOT EXISTS bd_pruebas_frases
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 2. Usar la base de datos
USE bd_pruebas_frases;

-- 3. Crear la tabla de frases
CREATE TABLE IF NOT EXISTS frases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    texto VARCHAR(500) NOT NULL,
    autor VARCHAR(200),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Insertar frases de muestra
INSERT INTO frases (texto, autor) VALUES
('La vida es aquello que te ocurre mientras estás ocupado haciendo otros planes.', 'John Lennon'),
('El éxito es la suma de pequeños esfuerzos repetidos día tras día.', 'Robert Collier'),
('No cuentes los días, haz que los días cuenten.', 'Muhammad Ali'),
('La simplicidad es la máxima sofisticación.', 'Leonardo da Vinci'),
('El conocimiento es poder.', 'Francis Bacon'),
('Si buscas resultados distintos, no hagas siempre lo mismo.', 'Albert Einstein'),
('La imaginación lo es todo. Es la vista previa de las próximas atracciones de la vida.', 'Albert Einstein'),
('No dejes para mañana lo que puedas hacer hoy.', 'Benjamin Franklin'),
('Nunca es tarde para ser lo que podrías haber sido.', 'George Eliot'),
('El futuro pertenece a quienes creen en la belleza de sus sueños.', 'Eleanor Roosevelt');

