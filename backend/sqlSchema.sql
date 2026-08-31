CREATE DATABASE IF NOT EXISTS smartscheme;

USE smartscheme;

DROP TABLE IF EXISTS users;

CREATE TABLE users (

    -- =========================
    -- ACCOUNT
    -- =========================
    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(150) UNIQUE NOT NULL,

    password VARCHAR(255) NOT NULL,


    -- =========================
    -- COMMON QUESTIONNAIRE
    -- NULL UNTIL PROFILE COMPLETED
    -- =========================

    age INT NULL,

    gender VARCHAR(20) NULL,

    state VARCHAR(100) NULL,

    district VARCHAR(100) NULL,

    marital_status VARCHAR(30) NULL,

    disability_status BOOLEAN NULL,

    annual_income DECIMAL(12,2) NULL,

    is_bpl BOOLEAN NULL,

    rural_urban VARCHAR(10) NULL,

    caste_category VARCHAR(30) NULL,

    loan_required BOOLEAN NULL,

    house_ownership BOOLEAN NULL,

    occupation VARCHAR(50) NULL,


    -- =========================
    -- STUDENT QUESTIONS
    -- =========================

    education_level VARCHAR(100) NULL,

    course VARCHAR(150) NULL,

    year_of_study VARCHAR(30) NULL,

    institution_type VARCHAR(50) NULL,

    current_scholarship BOOLEAN NULL,


    -- =========================
    -- FARMER QUESTIONS
    -- =========================

    land_owner BOOLEAN NULL,

    land_holding DECIMAL(10,2) NULL,

    farming_type VARCHAR(100) NULL,

    irrigation_available BOOLEAN NULL,

    agricultural_loan BOOLEAN NULL,


    -- =========================
    -- BUSINESS QUESTIONS
    -- =========================

    business_type VARCHAR(100) NULL,

    business_registered BOOLEAN NULL,

    business_age DECIMAL(5,2) NULL,

    business_turnover DECIMAL(14,2) NULL,

    business_financial_need BOOLEAN NULL,


    -- =========================
    -- HOMEMAKER QUESTIONS
    -- =========================

    skills TEXT NULL,

    home_based_business BOOLEAN NULL,

    business_interest BOOLEAN NULL,


    -- =========================
    -- PROFILE STATUS
    -- =========================

    profile_completed BOOLEAN DEFAULT FALSE,

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