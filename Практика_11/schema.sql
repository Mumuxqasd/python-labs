PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    host TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('online', 'offline', 'maintenance')),
    cpu_load REAL NOT NULL CHECK(cpu_load >= 0 AND cpu_load <= 100)
);

CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    cpu_load REAL NOT NULL CHECK(cpu_load >= 0 AND cpu_load <= 100),
    memory_load REAL NOT NULL CHECK(memory_load >= 0 AND memory_load <= 100),
    captured_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(server_id) REFERENCES servers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS server_tags (
    server_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY(server_id, tag_id),
    FOREIGN KEY(server_id) REFERENCES servers(id) ON DELETE CASCADE,
    FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_servers_status ON servers(status);
CREATE INDEX IF NOT EXISTS idx_metrics_server_time ON metrics(server_id, captured_at);
