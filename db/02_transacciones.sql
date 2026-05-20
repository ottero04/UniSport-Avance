
CREATE TABLE IF NOT EXISTS transacciones (
    id           INTEGER PRIMARY KEY AUTO_INCREMENT,
    id_usuario   INTEGER NOT NULL,
    tipo         TEXT NOT NULL,
    monto        REAL NOT NULL,
    fecha        DATETIME DEFAULT CURRENT_TIMESTAMP,
    descripcion  TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

INSERT INTO transacciones (id_usuario, tipo, monto, descripcion) VALUES
(1, 'deposito', 200.00, 'Depósito inicial'),
(2, 'deposito', 300.00, 'Recarga'),
(3, 'retiro', 50.00, 'Retiro a cuenta bancaria'),
(4, 'ganancia', 120.50, 'Ganancia apuesta'),
(5, 'perdida', 80.00, 'Pérdida apuesta'),
(6, 'deposito', 150.00, 'Bono recarga'),
(7, 'retiro', 200.00, 'Retiro parcial'),
(8, 'ganancia', 75.25, 'Ganancia múltiple'),
(9, 'perdida', 30.00, 'Apuesta perdida'),
(10, 'deposito', 500.00, 'Depósito grande');