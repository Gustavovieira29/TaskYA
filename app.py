from datetime import date, datetime
from typing import Any, Dict, List

from flask import Flask, redirect, render_template, request, url_for
from database import db, Task

app = Flask(__name__)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar o banco de dados com a aplicação
db.init_app(app)

# Criar as tabelas se não existirem
with app.app_context():
    db.create_all()


def read_tasks() -> List[Dict[str, Any]]:
    """Lê todas as tarefas do banco de dados."""
    tasks = Task.query.all()
    return [task.to_dict() for task in tasks]


def get_sorted_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ordena tarefas por data (mais recentes primeiro)."""
    return sorted(tasks, key=lambda task: task["date"], reverse=True)


def filter_tasks(tasks: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    """Filtra tarefas por status."""
    if status == "completed":
        return [task for task in tasks if task["completed"]]
    if status == "pending":
        return [task for task in tasks if not task["completed"]]
    return tasks


def parse_date(value: str) -> date:
    """Converte string para date."""
    try:
        return date.fromisoformat(value)
    except ValueError:
        return date.today()


@app.route("/")
def index():
    filter_status = request.args.get("filter", "all")
    selected_date_str = request.args.get("selected_date", "")
    edit_id = request.args.get("edit_id", "")

    tasks = read_tasks()
    filtered_tasks = filter_tasks(tasks, filter_status)
    sorted_tasks = get_sorted_tasks(filtered_tasks)

    selected_date = None
    selected_date_tasks = []
    if selected_date_str:
        selected_date = parse_date(selected_date_str)
        selected_date_tasks = [
            task for task in tasks if parse_date(task["date"]) == selected_date
        ]

    stats = {
        "total": len(tasks),
        "completed": sum(1 for task in tasks if task["completed"]),
        "pending": sum(1 for task in tasks if not task["completed"]),
    }

    return render_template(
        "index.html",
        tasks=sorted_tasks,
        filter_status=filter_status,
        stats=stats,
        selected_date=selected_date,
        selected_date_tasks=selected_date_tasks,
        edit_id=edit_id,
    )


@app.route("/add", methods=["POST"])
def add_task():
    """Adiciona uma nova tarefa ao banco de dados."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    task_date = request.form.get("date", date.today().isoformat())

    if not title:
        return redirect(url_for("index"))

    try:
        new_task = Task(
            title=title,
            description=description,
            date=parse_date(task_date),
            completed=False
        )
        db.session.add(new_task)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao adicionar tarefa: {e}")
        db.session.rollback()

    return redirect(url_for("index"))


@app.route("/toggle/<task_id>", methods=["POST"])
def toggle_task(task_id: str):
    """Alterna o status de conclusão de uma tarefa."""
    try:
        task = Task.query.get(task_id)
        if task:
            task.completed = not task.completed
            db.session.commit()
    except Exception as e:
        print(f"Erro ao alternar tarefa: {e}")
        db.session.rollback()

    return redirect(request.referrer or url_for("index"))


@app.route("/delete/<task_id>", methods=["POST"])
def delete_task(task_id: str):
    """Deleta uma tarefa do banco de dados."""
    try:
        task = Task.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
    except Exception as e:
        print(f"Erro ao deletar tarefa: {e}")
        db.session.rollback()

    return redirect(request.referrer or url_for("index"))


@app.route("/update/<task_id>", methods=["POST"])
def update_task(task_id: str):
    """Atualiza os dados de uma tarefa."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if not title:
        return redirect(url_for("index"))

    try:
        task = Task.query.get(task_id)
        if task:
            task.title = title
            task.description = description
            db.session.commit()
    except Exception as e:
        print(f"Erro ao atualizar tarefa: {e}")
        db.session.rollback()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
