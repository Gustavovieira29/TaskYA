"""Script para inicializar o banco de dados com dados de exemplo."""

from app import app, db, Task
from datetime import date, timedelta


def init_database():
    """Inicializa o banco de dados e adiciona dados de exemplo."""
    with app.app_context():
        # Criar as tabelas
        db.create_all()
        
        # Limpar dados existentes (opcional)
        Task.query.delete()
        db.session.commit()
        
        # Adicionar tarefas de exemplo
        example_tasks = [
            Task(
                title="Revisar código do projeto",
                description="Fazer review do código antes do merge para produção",
                date=date.today(),
                completed=False
            ),
            Task(
                title="Documentar API",
                description="Adicionar documentação Swagger para os endpoints",
                date=date.today() + timedelta(days=1),
                completed=False
            ),
            Task(
                title="Testes unitários",
                description="Escrever testes para novas funcionalidades",
                date=date.today() + timedelta(days=2),
                completed=True
            ),
            Task(
                title="Deploy em staging",
                description="Fazer deploy da versão 2.0 no ambiente staging",
                date=date.today() + timedelta(days=3),
                completed=False
            ),
            Task(
                title="Reunião com cliente",
                description="Apresentar novas features do sistema",
                date=date.today() - timedelta(days=1),
                completed=True
            ),
        ]
        
        for task in example_tasks:
            db.session.add(task)
        
        db.session.commit()
        
        print("✓ Banco de dados inicializado com sucesso!")
        print(f"✓ {len(example_tasks)} tarefas de exemplo adicionadas")
        
        # Listar as tarefas
        all_tasks = Task.query.all()
        print(f"\nTarefas no banco de dados ({len(all_tasks)}):")
        for task in all_tasks:
            status = "✓ Concluída" if task.completed else "○ Pendente"
            print(f"  - [{status}] {task.title} ({task.date})")


if __name__ == "__main__":
    init_database()
