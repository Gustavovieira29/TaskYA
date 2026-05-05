# Guia de Banco de Dados - TaskYA

## Informações Gerais

- **SGBD**: SQLite 3
- **ORM**: SQLAlchemy com Flask-SQLAlchemy
- **Localização**: `instance/tasks.db`
- **Backup**: `instance/tasks.db.backup`

## Estrutura das Tabelas

### Tabela: `tasks`

Armazena todas as tarefas do sistema.

| Campo | Tipo | Restrições | Descrição |
|-------|------|-----------|-----------|
| id | VARCHAR(36) | PRIMARY KEY | UUID único da tarefa |
| title | VARCHAR(200) | NOT NULL | Título da tarefa |
| description | TEXT | NULLABLE | Descrição detalhada |
| date | DATE | NOT NULL | Data da tarefa |
| completed | BOOLEAN | DEFAULT FALSE | Status de conclusão |
| created_at | DATETIME | NOT NULL | Timestamp de criação |
| updated_at | DATETIME | NOT NULL | Timestamp da última atualização |

## Índices

Para melhor performance:

```sql
CREATE INDEX idx_tasks_date ON tasks(date);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
```

## Views Disponíveis

### `pending_tasks`
Visualiza todas as tarefas pendentes (não concluídas).

```sql
SELECT * FROM pending_tasks;
```

### `completed_tasks`
Visualiza todas as tarefas concluídas.

```sql
SELECT * FROM completed_tasks;
```

### `task_stats`
Estatísticas gerais de tarefas.

```sql
SELECT * FROM task_stats;
```

## Operações CRUD

### CREATE (Adicionar Tarefa)

```python
# Via Interface Web
POST /add
  title: "Título da tarefa"
  description: "Descrição opcional"
  date: "2026-05-04"
```

### READ (Listar Tarefas)

```python
# Via Interface Web
GET /
  # Filtros opcionais:
  filter: "all" | "pending" | "completed"
  selected_date: "2026-05-04"
```

### UPDATE (Atualizar Tarefa)

```python
# Via Interface Web
POST /update/<task_id>
  title: "Novo título"
  description: "Nova descrição"
```

### DELETE (Remover Tarefa)

```python
# Via Interface Web
POST /delete/<task_id>
```

### TOGGLE (Marcar Concluída/Pendente)

```python
# Via Interface Web
POST /toggle/<task_id>
```

## Backup e Restauração

### Criar Backup

```bash
cp instance/tasks.db instance/tasks.db.backup
```

### Restaurar Backup

```bash
cp instance/tasks.db.backup instance/tasks.db
```

### Reinicializar com Dados de Exemplo

```bash
python init_db.py
```

## Acesso Direto ao Banco de Dados

### Query SQL Direta (SQLite)

```bash
sqlite3 instance/tasks.db
```

### Exemplos de Queries

**Listar todas as tarefas**
```sql
SELECT id, title, date, completed FROM tasks ORDER BY date DESC;
```

**Contar tarefas por status**
```sql
SELECT completed, COUNT(*) FROM tasks GROUP BY completed;
```

**Tarefas de uma data específica**
```sql
SELECT * FROM tasks WHERE date = '2026-05-04';
```

**Tarefas atrasadas**
```sql
SELECT * FROM tasks WHERE date < date('now') AND completed = FALSE;
```

## Migrações e Alterações de Schema

Para alterar o schema do banco de dados, modifique o modelo em `database.py`:

```python
class Task(db.Model):
    __tablename__ = 'tasks'
    # ... campos existentes
    # novo_campo = db.Column(db.String(100), default='valor')
```

Depois reinicialize o banco:
```bash
python init_db.py
```

## Troubleshooting

### Banco de Dados Corrompido

Se o banco estiver corrompido ou tiver problemas:

1. Delete o arquivo `instance/tasks.db`
2. Execute `python init_db.py` para recriar com dados de exemplo
3. Ou restaure do backup: `cp instance/tasks.db.backup instance/tasks.db`

### Resetar Banco de Dados

```bash
rm instance/tasks.db
python init_db.py
```

### Verificar Integridade

```bash
sqlite3 instance/tasks.db "PRAGMA integrity_check;"
```

## Performance

- Índices criados automaticamente nas colunas `date`, `completed` e `created_at`
- Para grandes volumes, considerar adicionar paginação
- SQLite é adequado para até ~10M de registros
- Para aplicações maiores, migrar para PostgreSQL

## Segurança

- Todas as queries usam SQLAlchemy ORM (prevenção de SQL injection)
- Entrada de usuário é validada antes de ser salva
- Timestamps são gerenciados automaticamente pelo banco
