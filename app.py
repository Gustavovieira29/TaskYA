from datetime import date, datetime
from typing import Any, Dict, List
import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from database import db, Task
from audit_log import log_create, log_update, log_delete, log_toggle, log_error

# LangChain: carrega variáveis de ambiente e habilita o uso do Groq através do framework
load_dotenv()

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
    print(f"read_tasks: found {len(tasks)} tasks")
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


def generate_task_summary(tasks: List[Dict[str, Any]]) -> str:
    """Gera um resumo das tarefas usando LangChain."""
    if not tasks:
        return "Nenhuma tarefa disponível para gerar resumo."

    try:
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0.3
        )
        prompt = ChatPromptTemplate.from_messages([
            HumanMessagePromptTemplate.from_template(
                "Resuma estas tarefas em até 5 frases, destacando pendências importantes:\n\n{tasks}"
            )
        ])
        chain = prompt | llm
        task_text = "\n".join(
            f"- [{'x' if task['completed'] else ' '}] {task['title']} ({task['date']}): {task['description'] or 'sem descrição'}"
            for task in tasks
        )
        return chain.invoke({"tasks": task_text}).content.strip()
    except Exception as e:
        log_error("LANGCHAIN_SUMMARY", e)
        return f"Erro ao gerar resumo: {str(e)}"


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


@app.route("/generate_summary")
def generate_summary():
    """Endpoint simples para gerar um resumo de tarefas via LangChain."""
    tasks = read_tasks()
    sorted_tasks = get_sorted_tasks(tasks)
    print(f"Route: tasks count: {len(sorted_tasks)}")
    summary = generate_task_summary(sorted_tasks)
    return summary, 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/add", methods=["POST"])
def add_task():
    """Adiciona uma nova tarefa ao banco de dados."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    task_date = request.form.get("date", date.today().isoformat())

    # Validações
    if not title:
        log_error("ADD_TASK", Exception("Título vazio"))
        return redirect(url_for("index"))

    if len(title) > 200:
        log_error("ADD_TASK", Exception("Título muito longo (máx 200 caracteres)"))
        title = title[:200]

    if len(description) > 5000:
        log_error("ADD_TASK", Exception("Descrição muito longa (máx 5000 caracteres)"))
        description = description[:5000]

    try:
        new_task = Task(
            title=title,
            description=description,
            date=parse_date(task_date),
            completed=False
        )
        db.session.add(new_task)
        db.session.commit()
        
        # Registrar no log
        log_create(new_task.id, title, task_date)
        
    except Exception as e:
        log_error("ADD_TASK", e)
        db.session.rollback()

    return redirect(url_for("index"))


@app.route("/toggle/<task_id>", methods=["POST"])
def toggle_task(task_id: str):
    """Alterna o status de conclusão de uma tarefa."""
    try:
        task = Task.query.get(task_id)
        if task:
            old_status = task.completed
            task.completed = not task.completed
            db.session.commit()
            
            # Registrar no log
            log_toggle(task_id, task.title, task.completed)
        else:
            log_error("TOGGLE_TASK", Exception(f"Tarefa não encontrada: {task_id}"))
    except Exception as e:
        log_error("TOGGLE_TASK", e)
        db.session.rollback()

    return redirect(request.referrer or url_for("index"))


@app.route("/delete/<task_id>", methods=["POST"])
def delete_task(task_id: str):
    """Deleta uma tarefa do banco de dados."""
    try:
        task = Task.query.get(task_id)
        if task:
            task_title = task.title
            db.session.delete(task)
            db.session.commit()
            
            # Registrar no log
            log_delete(task_id, task_title)
        else:
            log_error("DELETE_TASK", Exception(f"Tarefa não encontrada: {task_id}"))
    except Exception as e:
        log_error("DELETE_TASK", e)
        db.session.rollback()

    return redirect(request.referrer or url_for("index"))


@app.route("/update/<task_id>", methods=["POST"])
def update_task(task_id: str):
    """Atualiza os dados de uma tarefa."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if not title:
        log_error("UPDATE_TASK", Exception("Título vazio"))
        return redirect(url_for("index"))

    if len(title) > 200:
        title = title[:200]

    try:
        task = Task.query.get(task_id)
        if task:
            # Registrar mudanças no log
            if task.title != title:
                log_update(task_id, "title", task.title, title)
            if task.description != description:
                log_update(task_id, "description", task.description[:50], description[:50])
            
            task.title = title
            task.description = description
            db.session.commit()
        else:
            log_error("UPDATE_TASK", Exception(f"Tarefa não encontrada: {task_id}"))
    except Exception as e:
        log_error("UPDATE_TASK", e)
        db.session.rollback()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
