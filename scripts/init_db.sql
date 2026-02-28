-- OA Agent MySQL 初始化脚本
-- 执行: mysql -u root -p < scripts/init_db.sql

CREATE DATABASE IF NOT EXISTS oa_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE oa_agent;

-- 请假申请表
CREATE TABLE IF NOT EXISTS leave_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee VARCHAR(128) NOT NULL,
    days INT NOT NULL,
    reason TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_employee (employee),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 报销申请表
CREATE TABLE IF NOT EXISTS expense_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee VARCHAR(128) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    category VARCHAR(64),
    reason TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_employee (employee),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Agent 审计日志
CREATE TABLE IF NOT EXISTS agent_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_input TEXT,
    skill VARCHAR(64),
    action TEXT,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_skill (skill),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
