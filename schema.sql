

CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority in ('Bassa', 'Media', 'Alta')),
    status TEXT NOT NULL CHECK (status in ('Aperta', 'In lavorazione', 'In attesa', 'Completata')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notes(
id INTEGER PRIMARY KEY AUTOINCREMENT,
task_id INTEGER NOT NULL,
created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
content TEXT NOT NULL,
FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS status_history(
id INTEGER PRIMARY KEY AUTOINCREMENT,
task_id INTEGER NOT NULL,
from_status TEXT,
to_status TEXT NOT NULL CHECK (to_status in ('Aperta', 'In lavorazione', 'In attesa', 'Completata')),
changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_status ON tasks(user_id, status);
CREATE INDEX IF NOT EXISTS idx_user_duedate ON tasks(user_id, due_date);
CREATE INDEX IF NOT EXISTS idx_notes_task_created ON notes(task_id, created_at);
CREATE INDEX IF NOT EXISTS idx_status_task_changed ON status_history(task_id, changed_at);
