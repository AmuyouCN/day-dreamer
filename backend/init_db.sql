-- 接口自动化测试平台数据库初始化脚本
-- 创建数据库和表结构，插入初始数据

-- 创建数据库
CREATE DATABASE IF NOT EXISTS test_platform_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE test_platform_dev;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login DATETIME NULL,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 角色表
CREATE TABLE IF NOT EXISTS roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 权限表
CREATE TABLE IF NOT EXISTS permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_resource_action (resource, action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 用户角色关联表
CREATE TABLE IF NOT EXISTS user_roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_role (user_id, role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 角色权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_role_permission (role_id, permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 环境表
CREATE TABLE IF NOT EXISTS environments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    config JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 接口定义表
CREATE TABLE IF NOT EXISTS api_definitions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    method VARCHAR(10) NOT NULL,
    url VARCHAR(500) NOT NULL,
    headers JSON,
    query_params JSON,
    body_schema JSON,
    response_schema JSON,
    creator_id INT NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id),
    INDEX idx_creator (creator_id),
    INDEX idx_method_url (method, url(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 测试用例表
CREATE TABLE IF NOT EXISTS test_cases (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    api_id INT NOT NULL,
    request_data JSON,
    expected_response JSON,
    assertions JSON,
    creator_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (api_id) REFERENCES api_definitions(id) ON DELETE CASCADE,
    FOREIGN KEY (creator_id) REFERENCES users(id),
    INDEX idx_api (api_id),
    INDEX idx_creator (creator_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 变量表
CREATE TABLE IF NOT EXISTS variables (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    value TEXT,
    type VARCHAR(20) NOT NULL DEFAULT 'string',
    scope VARCHAR(20) NOT NULL,
    user_id INT NULL,
    environment_id INT NULL,
    description VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (environment_id) REFERENCES environments(id) ON DELETE CASCADE,
    INDEX idx_scope (scope),
    INDEX idx_user_id (user_id),
    INDEX idx_environment_id (environment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 测试执行表
CREATE TABLE IF NOT EXISTS test_executions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    execution_type VARCHAR(20) NOT NULL,
    target_id INT NOT NULL,
    executor_id INT NOT NULL,
    environment_id INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    started_at DATETIME NULL,
    finished_at DATETIME NULL,
    execution_config JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (executor_id) REFERENCES users(id),
    FOREIGN KEY (environment_id) REFERENCES environments(id),
    INDEX idx_executor (executor_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 测试结果表
CREATE TABLE IF NOT EXISTS test_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    execution_id INT NOT NULL,
    test_case_id INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    request_data JSON,
    response_data JSON,
    assertion_results JSON,
    duration FLOAT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES test_executions(id) ON DELETE CASCADE,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id),
    INDEX idx_execution (execution_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入初始数据

-- 插入默认环境
INSERT INTO environments (name, description, config) VALUES 
('development', '开发环境', '{"base_url": "http://localhost:8000"}'),
('testing', '测试环境', '{"base_url": "http://test.example.com"}'),
('production', '生产环境', '{"base_url": "https://api.example.com"}');

-- 插入默认角色
INSERT INTO roles (name, description) VALUES 
('管理员', '系统管理员，拥有所有权限'),
('测试负责人', '测试项目负责人'),
('高级测试工程师', '高级测试工程师'),
('测试工程师', '一般测试工程师'),
('实习生', '实习生，只读权限');

-- 插入权限
INSERT INTO permissions (name, resource, action, description) VALUES 
('user:read', 'user', 'read', '查看用户信息'),
('user:write', 'user', 'write', '编辑用户信息'),
('user:delete', 'user', 'delete', '删除用户'),
('user:self', 'user', 'self', '管理自己的信息'),
('role:read', 'role', 'read', '查看角色信息'),
('role:write', 'role', 'write', '编辑角色信息'),
('permission:read', 'permission', 'read', '查看权限信息'),
('api:read', 'api', 'read', '查看接口定义'),
('api:write', 'api', 'write', '编辑接口定义'),
('api:delete', 'api', 'delete', '删除接口定义'),
('test:execute', 'test', 'execute', '执行测试'),
('test:manage', 'test', 'manage', '管理测试用例'),
('test:read', 'test', 'read', '查看测试信息'),
('report:read', 'report', 'read', '查看测试报告'),
('variable:global', 'variable', 'global', '管理全局变量'),
('variable:personal', 'variable', 'personal', '管理个人变量'),
('system:admin', 'system', 'admin', '系统管理权限');

-- 创建默认管理员用户 (密码: admin123)
INSERT INTO users (username, email, password_hash, full_name, is_active) VALUES 
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewFBo3A1Qv0Q1JXW', '系统管理员', true);

-- 创建默认测试用户 (密码: test123)
INSERT INTO users (username, email, password_hash, full_name, is_active) VALUES 
('tester', 'tester@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewFBo3A1Qv0Q1JXW', '测试用户', true);

-- 分配管理员角色
INSERT INTO user_roles (user_id, role_id) VALUES 
(1, 1), -- admin -> 管理员
(2, 4); -- tester -> 测试工程师

-- 管理员拥有所有权限
INSERT INTO role_permissions (role_id, permission_id) 
SELECT 1, id FROM permissions;

-- 测试工程师基本权限
INSERT INTO role_permissions (role_id, permission_id) VALUES 
(4, (SELECT id FROM permissions WHERE name = 'user:self')),
(4, (SELECT id FROM permissions WHERE name = 'api:read')),
(4, (SELECT id FROM permissions WHERE name = 'api:write')),
(4, (SELECT id FROM permissions WHERE name = 'test:execute')),
(4, (SELECT id FROM permissions WHERE name = 'test:manage')),
(4, (SELECT id FROM permissions WHERE name = 'test:read')),
(4, (SELECT id FROM permissions WHERE name = 'report:read')),
(4, (SELECT id FROM permissions WHERE name = 'variable:personal'));

-- 测试负责人权限（包含测试工程师权限 + 管理权限）
INSERT INTO role_permissions (role_id, permission_id) VALUES 
(2, (SELECT id FROM permissions WHERE name = 'user:read')),
(2, (SELECT id FROM permissions WHERE name = 'user:self')),
(2, (SELECT id FROM permissions WHERE name = 'role:read')),
(2, (SELECT id FROM permissions WHERE name = 'api:read')),
(2, (SELECT id FROM permissions WHERE name = 'api:write')),
(2, (SELECT id FROM permissions WHERE name = 'api:delete')),
(2, (SELECT id FROM permissions WHERE name = 'test:execute')),
(2, (SELECT id FROM permissions WHERE name = 'test:manage')),
(2, (SELECT id FROM permissions WHERE name = 'test:read')),
(2, (SELECT id FROM permissions WHERE name = 'report:read')),
(2, (SELECT id FROM permissions WHERE name = 'variable:global')),
(2, (SELECT id FROM permissions WHERE name = 'variable:personal'));

-- 高级测试工程师权限
INSERT INTO role_permissions (role_id, permission_id) VALUES 
(3, (SELECT id FROM permissions WHERE name = 'user:self')),
(3, (SELECT id FROM permissions WHERE name = 'api:read')),
(3, (SELECT id FROM permissions WHERE name = 'api:write')),
(3, (SELECT id FROM permissions WHERE name = 'test:execute')),
(3, (SELECT id FROM permissions WHERE name = 'test:manage')),
(3, (SELECT id FROM permissions WHERE name = 'test:read')),
(3, (SELECT id FROM permissions WHERE name = 'report:read')),
(3, (SELECT id FROM permissions WHERE name = 'variable:personal'));

-- 实习生权限（只读）
INSERT INTO role_permissions (role_id, permission_id) VALUES 
(5, (SELECT id FROM permissions WHERE name = 'user:self')),
(5, (SELECT id FROM permissions WHERE name = 'api:read')),
(5, (SELECT id FROM permissions WHERE name = 'test:read')),
(5, (SELECT id FROM permissions WHERE name = 'report:read'));

-- 插入一些示例全局变量
INSERT INTO variables (name, value, type, scope, description) VALUES 
('base_timeout', '30', 'number', 'global', '默认超时时间（秒）'),
('default_headers', '{"Content-Type": "application/json", "Accept": "application/json"}', 'json', 'global', '默认请求头'),
('api_version', 'v1', 'string', 'global', 'API版本号');

COMMIT;