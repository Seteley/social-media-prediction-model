
-- Inserciones para la tabla empresa
INSERT INTO empresa (id_empresa, nombre, fecha_registro) VALUES
  (1, 'Interbank', DATE '2025-07-10'),
  (2, 'BanBif', DATE '2025-07-10'),
  (3, 'BancodelaNacion', DATE '2025-07-10'),
  (4, 'BCRP', DATE '2025-07-10'),
  (5, 'BancoPichincha', DATE '2025-07-10'),
  (6, 'BBVA', DATE '2025-07-10'),
  (7, 'BCP', DATE '2025-07-10'),
  (8, 'ScotiabankPE', DATE '2025-07-10');

-- Inserciones para la tabla usuario (cuentas sociales asociadas a empresa)
INSERT INTO usuario (id_usuario, id_empresa, cuenta, nombre, fecha_registro) VALUES
  (1, 1, 'Interbank', 'Interbank', DATE '2025-07-10'),
  (2, 2, 'BanBif', 'Banco Interamericano de Finanzas (BanBif)', DATE '2025-07-10'),
  (3, 3, 'BancodelaNacion', 'Banco de la Nación', DATE '2025-07-10'),
  (4, 4, 'bcrpoficial', 'Banco Central de Reserva del Perú (BCRP)', DATE '2025-07-10'),
  (5, 5, 'BancoPichincha', 'Banco Pichincha', DATE '2025-07-10'),
  (6, 6, 'bbva_peru', 'BBVA Perú', DATE '2025-07-10'),
  (7, 7, 'BCPComunica', 'Banco de Crédito del Perú (BCP)', DATE '2025-07-10'),
  (8, 8, 'ScotiabankPE', 'Scotiabank Perú', DATE '2025-07-10');
