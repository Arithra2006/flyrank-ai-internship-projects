CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN DEFAULT FALSE
);


INSERT INTO tasks (title, done)
VALUES
('Study FastAPI', false),
('Complete Assignment', false),
('Watch Movie', true)
ON CONFLICT DO NOTHING;