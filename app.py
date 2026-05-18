from datetime import date, datetime
from typing import Any, Dict, List, Optional
import os
import json

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for, jsonify
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from database import db, Task
from audit_log import log_create, log_update, log_delete, log_toggle, log_error
from prompt_engine import get_prompt_engine, PromptRequest
from prompt_modes import AIMode, AIModesConfig
from prompt_types import PromptType, PromptContext
from prompt_security import validate_and_sanitize_prompt, PromptSecurityValidator
from dual_api_manager import APIProvider

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

# Inicializar motor de prompts
prompt_engine = get_prompt_engine()


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


def generate_task_summary(tasks: List[Dict[str, Any]], mode: Optional[str] = None) -> str:
    """Gera um resumo das tarefas usando o novo motor de prompts."""
    if not tasks:
        return "Nenhuma tarefa disponível para gerar resumo."

    try:
        # Preparar texto das tarefas
        task_text = "\n".join(
            f"- [{'x' if task['completed'] else ' '}] {task['title']} ({task['date']}): {task['description'] or 'sem descrição'}"
            for task in tasks
        )

        # Criar requisição
        user_message = f"Resuma estas tarefas em até 5 frases, destacando pendências importantes:\n\n{task_text}"
        
        # Selecionar modo
        ai_mode = AIMode.SUMMARIZED  # Padrão para resumos
        if mode:
            mode_obj = AIModesConfig.get_mode_by_name(mode)
            if mode_obj:
                ai_mode = mode_obj
        
        request_obj = PromptRequest(
            user_message=user_message,
            mode=ai_mode,
            prompt_type=PromptType.STRUCTURED,
            context={"output_format": "Resumo em 5 frases máximo"}
        )

        # Processar
        response = prompt_engine.process_request(request_obj)
        return response.response_text
    except Exception as e:
        log_error("PROMPT_ENGINE_SUMMARY", e)
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


# ============= NOVOS ENDPOINTS - MOTOR DE PROMPTS =============

@app.route("/api/prompt/modes")
def get_ai_modes():
    """Retorna modos de IA disponíveis."""
    modes = AIModesConfig.get_all_modes()
    return jsonify({
        "modes": {
            mode_name: {
                "name": config.name,
                "description": config.description,
                "tone": config.tone,
                "focus": config.context_focus
            }
            for mode_name, config in modes.items()
        }
    })


@app.route("/api/prompt/analyze", methods=["POST"])
def analyze_prompt():
    """Analisa um prompt antes de processar."""
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Mensagem não fornecida"}), 400

    analysis = prompt_engine.analyze_request(user_message)
    return jsonify(analysis)


@app.route("/api/prompt/security-check", methods=["POST"])
def security_check():
    """Verifica segurança de um prompt."""
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Mensagem não fornecida"}), 400

    is_approved, clean_prompt, security_details = validate_and_sanitize_prompt(
        user_message, strict=True
    )

    return jsonify({
        "approved": is_approved,
        "clean_prompt": clean_prompt if is_approved else None,
        "security_score": PromptSecurityValidator.get_security_score(user_message),
        "threats": security_details
    })


@app.route("/api/prompt/process", methods=["POST"])
def process_prompt():
    """Processa um prompt com modo e tipo especificados."""
    data = request.get_json()
    user_message = data.get("message", "")
    mode = data.get("mode", "technical")
    prompt_type = data.get("prompt_type", "structured")
    provider = data.get("provider")

    if not user_message:
        return jsonify({"error": "Mensagem não fornecida"}), 400

    try:
        # Validar modo
        ai_mode = AIModesConfig.get_mode_by_name(mode) or AIMode.TECHNICAL
        
        # Validar tipo
        try:
            ptype = PromptType[prompt_type.upper()]
        except KeyError:
            ptype = PromptType.STRUCTURED

        # Validar provider
        preferred_provider = None
        if provider:
            try:
                preferred_provider = APIProvider[provider.upper()]
            except KeyError:
                pass

        # Criar requisição
        request_obj = PromptRequest(
            user_message=user_message,
            mode=ai_mode,
            prompt_type=ptype,
            preferred_provider=preferred_provider,
            context=data.get("context", {})
        )

        # Processar
        response = prompt_engine.process_request(request_obj)

        return jsonify({
            "success": response.metrics.success,
            "request_id": response.request_id,
            "response": response.response_text,
            "mode": response.mode.value,
            "metrics": response.metrics.to_dict(),
            "security_info": response.security_info
        })

    except Exception as e:
        log_error("PROCESS_PROMPT", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/prompt/compare", methods=["POST"])
def compare_providers():
    """Compara respostas de diferentes provedores."""
    data = request.get_json()
    user_message = data.get("message", "")
    mode = data.get("mode", "technical")
    prompt_type = data.get("prompt_type", "structured")

    if not user_message:
        return jsonify({"error": "Mensagem não fornecida"}), 400

    try:
        # Validar modo
        ai_mode = AIModesConfig.get_mode_by_name(mode) or AIMode.TECHNICAL
        
        # Validar tipo
        try:
            ptype = PromptType[prompt_type.upper()]
        except KeyError:
            ptype = PromptType.STRUCTURED

        # Criar requisição
        request_obj = PromptRequest(
            user_message=user_message,
            mode=ai_mode,
            prompt_type=ptype,
            context=data.get("context", {})
        )

        # Comparar
        comparison = prompt_engine.compare_providers(request_obj)

        return jsonify({
            "comparison": comparison,
            "request_id": request_obj.request_id
        })

    except Exception as e:
        log_error("COMPARE_PROVIDERS", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/prompt/task-summary", methods=["POST"])
def task_summary_advanced():
    """Gera resumo de tarefas com modo especificado."""
    data = request.get_json()
    mode = data.get("mode", "summarized")
    
    tasks = read_tasks()
    if not tasks:
        return jsonify({"summary": "Nenhuma tarefa disponível"}), 200

    summary = generate_task_summary(tasks, mode)
    return jsonify({
        "summary": summary,
        "mode": mode,
        "tasks_count": len(tasks)
    })


@app.route("/api/prompt/stats")
def prompt_statistics():
    """Retorna estatísticas de uso do motor de prompts."""
    stats = prompt_engine.get_statistics()
    return jsonify(stats)


@app.route("/api/prompt/history")
def prompt_history():
    """Retorna histórico de requisições e respostas."""
    limit = request.args.get("limit", default=10, type=int)
    
    return jsonify({
        "requests": prompt_engine.get_request_history(limit),
        "responses": prompt_engine.get_response_history(limit)
    })


@app.route("/api/prompt/providers")
def get_providers():
    """Retorna provedores de API disponíveis."""
    available = prompt_engine.get_available_providers()
    return jsonify({
        "providers": available,
        "count": len(available)
    })


@app.route("/api/prompt/clear-history", methods=["POST"])
def clear_prompt_history():
    """Limpa histórico de prompts."""
    try:
        prompt_engine.clear_history()
        return jsonify({"message": "Histórico limpo com sucesso"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
