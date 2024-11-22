CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(32) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL, 
    isAdmin BOOLEAN DEFAULT FALSE,
);

CREATE TABLE IF NOT EXISTS requests (
    id - SERIAL PRIMARY KEY,
    user_id - INTEGER REFERENCES users(id),
    os - VARCHAR(32),
    start_time - DATETIME,
    end_time - DATETIME,
);

CREATE TABLE IF NOT EXISTS servers (
    id - SERIAL PRIMARY KEY,
    user_id - INTEGER REFERENCES USERS(id),
    os - VARCHAR(32),
    start_time - DATETIME,
    end_time - DATETIME,
);


