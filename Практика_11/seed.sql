INSERT INTO servers(name, host, status, cpu_load) VALUES
('web-1', '10.0.0.11', 'online', 35),
('web-2', '10.0.0.12', 'online', 42),
('db-1', '10.0.0.21', 'offline', 0),
('db-2', '10.0.0.22', 'online', 61),
('cache-1', '10.0.0.31', 'online', 28),
('api-1', '10.0.0.41', 'maintenance', 15),
('api-2', '10.0.0.42', 'online', 53),
('worker-1', '10.0.0.51', 'online', 70),
('worker-2', '10.0.0.52', 'offline', 0),
('monitor-1', '10.0.0.61', 'online', 22);

INSERT INTO tags(name) VALUES ('production'), ('database'), ('web'), ('critical'), ('service');
INSERT INTO server_tags(server_id, tag_id) VALUES (1,1), (1,3), (3,2), (3,4), (4,2), (7,5);
INSERT INTO metrics(server_id, cpu_load, memory_load) VALUES (1,35,40), (2,42,45), (3,0,20), (4,61,68), (7,53,57);
