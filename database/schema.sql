-- Criação da tabela de vídeos
CREATE TABLE IF NOT EXISTS videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50),
    url TEXT,
    filename VARCHAR(255),
    status ENUM('pending', 'downloading', 'completed', 'error'),
    duration FLOAT,
    created_at DATETIME,
    updated_at DATETIME
);