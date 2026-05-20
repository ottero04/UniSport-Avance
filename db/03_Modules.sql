DROP TABLE IF EXISTS modules;

CREATE TABLE modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(100),
    code VARCHAR(10),
    status INTEGER DEFAULT 1,
    route VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO modules (description, code, status, route) VALUES
('Mi Perfil', 'profile', 1, '/profile'),
('Mis Apuestas', 'bets', 1, '/bets'),
('En Vivo', 'live', 1, '/online'),
('Eventos', 'events', 1, '/events');