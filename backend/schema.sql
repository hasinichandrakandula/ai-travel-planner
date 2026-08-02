-- Run this once to create the database, or just let SQLAlchemy's
-- Base.metadata.create_all() do it automatically on first backend run.

CREATE DATABASE IF NOT EXISTS travel_planner CHARACTER SET utf8mb4;
USE travel_planner;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS search_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    destination VARCHAR(150) NOT NULL,
    preferences VARCHAR(255),
    days INT DEFAULT 1,
    llm_summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
