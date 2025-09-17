-- Script SQL para insertar ingredientes en la base de datos
-- Tabla: ingredientes
-- Columnas: id (autoincremental), nombre, unidad_medida, valor_unidad, sitio_compra

-- Correr con: sqlite3 aplicacion.sqlite < insert_ingredientes.sql

INSERT INTO ingredientes (nombre, unidad_medida, valor_unidad, sitio_compra) VALUES
('Tomate chonto', 'libra', 5000, 'Fruver El mejor'),
('Cebolla larga', 'libra', 4000, 'Fruver El mejor'),
('Papa criolla', 'libra', 4090, 'Plaza Concordia'),
('Papa pastusa', 'libra', 1890, 'Plaza Concordia'),
('Aguacate', 'unidad', 5000, 'Plaza Concordia'),
('Berenjenas', 'libra', 3800, 'Plaza Concordia'),
('Pollo', 'libra', 8500, 'Carnicería Central'),
('Guascas', 'atado', 2000, 'Fruver El mejor'),
('Cilantro', 'atado', 1500, 'Fruver El mejor'),
('Ajo', 'libra', 6000, 'Fruver El mejor'),
('Mazorca', 'unidad', 3000, 'Plaza Concordia'),
('Mozzarella', 'libra', 12000, 'Supermercado'),
('Queso parmesano', 'libra', 15000, 'Supermercado'),
('Harina de trigo', 'libra', 2500, 'Supermercado'),
('Aceite de oliva', 'botella', 18000, 'Supermercado'),
('Sal', 'libra', 1200, 'Supermercado'),
('Pimienta', 'frasco', 8000, 'Supermercado'),
('Salsa de tomate', 'frasco', 4500, 'Supermercado');

-- Verificar los ingredientes insertados
SELECT * FROM ingredientes ORDER BY nombre;
