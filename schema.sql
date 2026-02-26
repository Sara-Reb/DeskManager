DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS status_history;

CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE tasks(
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

CREATE TABLE notes(
id INTEGER PRIMARY KEY AUTOINCREMENT,
task_id INTEGER NOT NULL,
created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
content TEXT NOT NULL,
FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE status_history(
id INTEGER PRIMARY KEY AUTOINCREMENT,
task_id INTEGER NOT NULL,
from_status TEXT,
to_status TEXT NOT NULL CHECK (to_status in ('Aperta', 'In lavorazione', 'In attesa', 'Completata')),
changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_status ON tasks(user_id, status);
CREATE INDEX idx_user_duedate ON tasks(user_id, due_date);
CREATE INDEX idx_notes_task_created ON notes(task_id, created_at);
CREATE INDEX idx_status_task_changed ON status_history(task_id, changed_at);
