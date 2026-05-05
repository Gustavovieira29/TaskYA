-- Estrutura do Banco de Dados - TaskYA
-- Sistema: SQLite
-- Descrição: Schema das tarefas do gerenciador pessoal

-- Tabela: tasks
-- Armazena todas as tarefas do sistema
CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    completed BOOLEAN DEFAULT FALSE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(date);
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);

-- View para tarefas pendentes
CREATE VIEW IF NOT EXISTS pending_tasks AS
SELECT * FROM tasks
WHERE completed = FALSE
ORDER BY date DESC;

-- View para tarefas concluídas
CREATE VIEW IF NOT EXISTS completed_tasks AS
SELECT * FROM tasks
WHERE completed = TRUE
ORDER BY date DESC;

-- View para estatísticas
CREATE VIEW IF NOT EXISTS task_stats AS
SELECT
    COUNT(*) as total_tasks,
    SUM(CASE WHEN completed = TRUE THEN 1 ELSE 0 END) as completed_count,
    SUM(CASE WHEN completed = FALSE THEN 1 ELSE 0 END) as pending_count,
    DATE('now') as generated_at;
