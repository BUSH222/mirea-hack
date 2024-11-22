CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(32) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL, 
    isAdmin BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    os VARCHAR(32),
    user_comment TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    accepted BOOLEAN DEFAULT NULL,
    requires_manual_approval BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS servers (
    id SERIAL PRIMARY KEY,
    os VARCHAR(32)
);

CREATE TABLE IF NOT EXISTS request_servers ( -- which request is currently working on what server
    request_id INTEGER REFERENCES requests(id),
    server_id INTEGER REFERENCES servers(id)
);

CREATE TABLE IF NOT EXISTS logs(
    id SERIAL PRIMARY KEY,
    log_time TIMESTAMP,
    log_text TEXT
);
