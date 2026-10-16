-- Reference SQL snapshot. The active application creates tables from
-- backend/app/db/models.py; this snapshot predates some model fields.
-- PRIMARY KEY identifies a row, UNIQUE rejects repeated values, and
-- FOREIGN KEY requires a referenced parent row. ON DELETE defines how
-- MySQL handles linked rows when a parent is removed. INDEX supports
-- lookups, while InnoDB supplies transaction and foreign-key support.

-- Internship Portal v2.0 MySQL Full Schema
-- Includes Student Module + Recruiter Module tables
-- Run this entire script in MySQL Workbench

CREATE DATABASE IF NOT EXISTS internship_portal;
USE internship_portal;

-- 1. USERS
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. RECRUITER_PROFILES
CREATE TABLE IF NOT EXISTS recruiter_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_logo VARCHAR(500),
    designation VARCHAR(255),
    phone VARCHAR(50),
    company_website VARCHAR(500),
    company_size VARCHAR(100),
    industry VARCHAR(255),
    bio TEXT,
    linkedin_url VARCHAR(500),
    location VARCHAR(255),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. STUDENTS
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    avatar_url VARCHAR(500),
    university VARCHAR(255),
    degree VARCHAR(255),
    field_of_study VARCHAR(255),
    graduation_year INT,
    cgpa FLOAT,
    bio TEXT,
    location VARCHAR(255),
    preferred_mode VARCHAR(50) DEFAULT 'Remote',
    expected_stipend VARCHAR(100),
    portfolio_url VARCHAR(500),
    github_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. DOCUMENTS
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    INDEX idx_docs_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. SKILLS
CREATE TABLE IF NOT EXISTS skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(100),
    INDEX idx_skills_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. STUDENT_SKILLS
CREATE TABLE IF NOT EXISTS student_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency_level VARCHAR(50) DEFAULT 'Intermediate',
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    INDEX idx_ss_student (student_id),
    INDEX idx_ss_skill (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. INTERNSHIPS
CREATE TABLE IF NOT EXISTS internships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recruiter_id INT,
    title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_logo VARCHAR(500),
    location VARCHAR(255) NOT NULL,
    mode VARCHAR(50) DEFAULT 'Remote',
    stipend_amount INT NOT NULL DEFAULT 0,
    stipend_currency VARCHAR(10) DEFAULT '₹',
    duration VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    eligibility TEXT,
    responsibilities TEXT,
    benefits TEXT,
    recruiter_name VARCHAR(255),
    recruiter_email VARCHAR(255),
    recruiter_title VARCHAR(255),
    skills_required VARCHAR(500),
    is_external BOOLEAN DEFAULT FALSE,
    external_link VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    deadline DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recruiter_id) REFERENCES recruiter_profiles(id) ON DELETE CASCADE,
    INDEX idx_internships_title (title),
    INDEX idx_internships_company (company_name),
    INDEX idx_internships_location (location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. APPLICATIONS
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    internship_id INT NOT NULL,
    status VARCHAR(50) DEFAULT 'Applied',
    cover_letter TEXT,
    resume_url VARCHAR(500),
    recruiter_notes TEXT,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE,
    INDEX idx_apps_student (student_id),
    INDEX idx_apps_internship (internship_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. INTERVIEWS
CREATE TABLE IF NOT EXISTS interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recruiter_id INT NOT NULL,
    application_id INT NOT NULL,
    internship_id INT,
    scheduled_at DATETIME NOT NULL,
    duration_minutes INT DEFAULT 30,
    interview_type VARCHAR(50) DEFAULT 'Video Call',
    meeting_link VARCHAR(500),
    notes TEXT,
    status VARCHAR(50) DEFAULT 'Scheduled',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recruiter_id) REFERENCES recruiter_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE SET NULL,
    INDEX idx_interviews_recruiter (recruiter_id),
    INDEX idx_interviews_application (application_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. NOTIFICATIONS
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_notif_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. SAVED_INTERNSHIPS
CREATE TABLE IF NOT EXISTS saved_internships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    internship_id INT NOT NULL,
    saved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE,
    INDEX idx_saved_student (student_id),
    INDEX idx_saved_internship (internship_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. MESSAGES
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_msg_sender (sender_id),
    INDEX idx_msg_receiver (receiver_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Verify tables created
SELECT TABLE_NAME, TABLE_ROWS FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'internship_portal'
ORDER BY TABLE_NAME;
