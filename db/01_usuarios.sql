
CREATE TABLE IF NOT EXISTS usuarios (
    id                INTEGER PRIMARY KEY AUTO_INCREMENT,   
    nombre           TEXT NOT NULL UNIQUE,
    nickname          TEXT NOT NULL,
    identificacion    TEXT NOT NULL UNIQUE,
    correo            TEXT NOT NULL UNIQUE,
    telefono          TEXT,
    password_hash     TEXT NOT NULL,
    saldo             REAL DEFAULT 0.0,
    fecha_registro    DATETIME DEFAULT CURRENT_TIMESTAMP,
    activo            INTEGER DEFAULT 1
);

INSERT INTO usuarios (nombre, nickname, identificacion, correo, telefono, password_hash, saldo, activo) VALUES
('usuario1', 'user1', 'ID001', 'user1@example.com', '600000001', 'hash_123', 150.75, 1),
('usuario2', 'user2', 'ID002', 'user2@example.com', '600000002', 'hash_123', 200.00, 1),
('usuario3', 'user3', 'ID003', 'user3@example.com', '600000003', 'hash_123', 320.50, 1),
('usuario4', 'user4', 'ID004', 'user4@example.com', '600000004', 'hash_123', 80.25, 1),
('usuario5', 'user5', 'ID005', 'user5@example.com', '600000005', 'hash_123', 500.00, 1),
('usuario6', 'user6', 'ID006', 'user6@example.com', '600000006', 'hash_123', 0.00, 1),
('usuario7', 'user7', 'ID007', 'user7@example.com', '600000007', 'hash_123', 1250.00, 1),
('usuario8', 'user8', 'ID008', 'user8@example.com', '600000008', 'hash_123', 43.30, 1),
('usuario9', 'user9', 'ID009', 'user9@example.com', '600000009', 'hash_123', 670.10, 1),
('usuario10', 'user10', 'ID010', 'user10@example.com', '600000010', 'hash_123', 999.99, 1);
