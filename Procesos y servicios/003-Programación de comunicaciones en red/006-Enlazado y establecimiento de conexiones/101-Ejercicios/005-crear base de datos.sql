CREATE DATABASE IF NOT EXISTS ollama_api
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ollama_api;


CREATE TABLE users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE plans (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255) NULL,
    queries_per_hour INT UNSIGNED NOT NULL DEFAULT 60,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE user_plans (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    plan_id INT UNSIGNED NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL DEFAULT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT fk_user_plans_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_user_plans_plan
        FOREIGN KEY (plan_id) REFERENCES plans(id)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE api_keys (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    api_key VARCHAR(64) NOT NULL UNIQUE,
    description VARCHAR(255) NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP NULL DEFAULT NULL,
    CONSTRAINT fk_api_keys_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


INSERT INTO plans (name, description, queries_per_hour)
VALUES ('basic', 'Plan básico con límite por defecto', 100);

INSERT INTO users (username, password, email)
VALUES ('jocarsa', 'jocarsa', 'info@jocarsa.com');


INSERT INTO user_plans (user_id, plan_id)
SELECT u.id, p.id
FROM users u
JOIN plans p ON p.name = 'basic'
WHERE u.username = 'jocarsa';


INSERT INTO api_keys (user_id, api_key, description)
SELECT id, 'TEST_API_KEY_JOCARSA_123', 'Clave inicial de pruebas'
FROM users
WHERE username = 'jocarsa';


USE ollama_api;

CREATE TABLE api_usage (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    api_key_id INT UNSIGNED NOT NULL,
    hour_start DATETIME NOT NULL,
    request_count INT UNSIGNED NOT NULL DEFAULT 0,
    CONSTRAINT fk_api_usage_api_key
        FOREIGN KEY (api_key_id) REFERENCES api_keys(id)
        ON DELETE CASCADE,
    UNIQUE KEY uk_api_usage_key_hour (api_key_id, hour_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;






