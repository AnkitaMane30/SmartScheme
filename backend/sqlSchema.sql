CREATE DATABASE smartscheme;

USE smartscheme;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,

    age INT,
    gender VARCHAR(20),
    education_level VARCHAR(50),
    income FLOAT,
    category VARCHAR(50),
    state VARCHAR(50),
    occupation VARCHAR(50),

    profile_completed INT DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE schemes (

    scheme_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    details TEXT,
    eligibility TEXT,
    benefits TEXT,
    exclusion TEXT,
    documents_required TEXT,
    application_process TEXT,
    category VARCHAR(100),
    state VARCHAR(100),
    department VARCHAR(255),
    status VARCHAR(50),
    start_date DATE,
    end_date DATE,
    launch_date DATE NULL,
    min_income DECIMAL(10,2),
    max_income DECIMAL(10,2),
    gender VARCHAR(20),
    min_age INT,
    max_age INT,
    target_group VARCHAR(255),
    last_date_to_apply DATE,
    application_link VARCHAR(500) UNIQUE,
    content_hash VARCHAR(255),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);