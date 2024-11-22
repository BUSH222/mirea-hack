-- Insert data into users
INSERT INTO users (name, password, isAdmin) VALUES
('admin1', 'hashed_password_1', TRUE),
('user1', 'hashed_password_2', FALSE),
('user2', 'hashed_password_3', FALSE),
('user3', 'hashed_password_4', FALSE);

-- Insert data into servers
INSERT INTO servers (os) VALUES
('Ubuntu 20.04'),
('CentOS 7'),
('Windows Server'),
('Debian 11');

-- Insert data into requests
INSERT INTO requests (id, user_id, os, user_comment, start_time, end_time, accepted, requires_manual_approval) VALUES
(1, 2, 'Ubuntu 22.04', 'Need a test environment', '2024-11-22 10:00:00', '2024-11-22 14:00:00', NULL, TRUE),
(2, 3, 'Windows 10', 'Install custom software', '2024-11-23 09:00:00', '2024-11-23 13:00:00', FALSE, TRUE),
(3, 4, 'CentOS 8', 'Database testing', '2024-11-24 08:00:00', '2024-11-24 12:00:00', NULL, FALSE),
(4, 3, 'Ubuntu 20.04', 'Web application testing', '2024-11-25 15:00:00', '2024-11-25 19:00:00', TRUE, FALSE);

-- Insert data into request_servers
INSERT INTO request_servers (request_id, server_id) VALUES
(1, 1), -- Request 1 uses Server 1
(2, 3), -- Request 2 uses Server 3
(3, 2), -- Request 3 uses Server 2
(4, 1); -- Request 4 also uses Server 1
