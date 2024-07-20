CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(50),
    email_verified_at TIMESTAMP WITH TIME ZONE,
    image_url VARCHAR(255)
);

CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(255) NOT NULL,
    account_type VARCHAR(255) NOT NULL,
    account_provider VARCHAR(255) NOT NULL,
    refresh_token TEXT,
    access_token TEXT,
    expires_at BIGINT,
    id_token TEXT,
    scope TEXT,
    session_state TEXT,
    token_type TEXT,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);