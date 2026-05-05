"""Script de demonstração do sistema de inserção e logging de dados."""

from app import app, db, Task
from audit_log import logger
from datetime import date, timedelta


def demo_operations():
    """Demonstra as operações de inserção no banco de dados."""
    
    with app.app_context():
        print("\n" + "="*60)
        print("DEMONSTRAÇÃO DO SISTEMA DE INSERÇÃO E AUDITORIA")
        print("="*60 + "\n")
        
        # Demonstração 1: CREATE
        print("📝 1. CRIANDO TAREFAS...")
        print("-" * 60)
        
        tasks_data = [
            ("Revisar código", "Verificar pull requests no GitHub", date.today()),
            ("Documentar API", "Adicionar docs Swagger", date.today() + timedelta(days=1)),
            ("Testes unitários", "Escrever testes para novo módulo", date.today() + timedelta(days=2)),
        ]
        
        created_tasks = []
        for title, desc, task_date in tasks_data:
            task = Task(
                title=title,
                description=desc,
                date=task_date,
                completed=False
            )
            db.session.add(task)
            db.session.commit()
            created_tasks.append(task)
            print(f"✓ Criada: {title} ({task_date})")
        
        # Demonstração 2: READ
        print("\n📖 2. LENDO TAREFAS...")
        print("-" * 60)
        
        all_tasks = Task.query.all()
        print(f"Total de tarefas no banco: {len(all_tasks)}")
        for task in all_tasks[-3:]:
            status = "✓" if task.completed else "○"
            print(f"  [{status}] {task.title} - {task.date}")
        
        # Demonstração 3: UPDATE
        print("\n✏️  3. ATUALIZANDO TAREFA...")
        print("-" * 60)
        
        if created_tasks:
            task = created_tasks[0]
            old_title = task.title
            task.title = "Revisar código com CI/CD"
            task.description = "Verificar pull requests e executar testes automatizados"
            db.session.commit()
            print(f"✓ Atualizada: '{old_title}' → '{task.title}'")
        
        # Demonstração 4: TOGGLE
        print("\n✅ 4. MARCANDO COMO CONCLUÍDA...")
        print("-" * 60)
        
        if created_tasks:
            task = created_tasks[1]
            task.completed = True
            db.session.commit()
            status = "✓ Concluída" if task.completed else "○ Pendente"
            print(f"✓ Status alterado: {task.title} → {status}")
        
        # Demonstração 5: DELETE
        print("\n🗑️  5. DELETANDO TAREFA...")
        print("-" * 60)
        
        if len(created_tasks) > 2:
            task = created_tasks[2]
            title = task.title
            db.session.delete(task)
            db.session.commit()
            print(f"✓ Deletada: {title}")
        
        # Resumo Final
        print("\n" + "="*60)
        print("RESUMO FINAL")
        print("="*60)
        
        final_tasks = Task.query.all()
        completed = sum(1 for t in final_tasks if t.completed)
        pending = sum(1 for t in final_tasks if not t.completed)
        
        print(f"\n📊 Estatísticas Finais:")
        print(f"   Total: {len(final_tasks)} tarefas")
        print(f"   Concluídas: {completed} ✓")
        print(f"   Pendentes: {pending} ○")
        print(f"\n📋 Logs salvos em: logs/operations_*.log")
        print("\n✅ Demonstração concluída!\n")


if __name__ == "__main__":
    demo_operations()
