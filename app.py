import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from flask import Flask, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "tasks.json"

app = Flask(__name__)


def read_tasks() -> List[Dict[str, Any]]:
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_tasks(tasks: List[Dict[str, Any]]) -> None:
    DATA_FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")


def get_sorted_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(tasks, key=lambda task: task["date"], reverse=True)


def filter_tasks(tasks: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    if status == "completed":
        return [task for task in tasks if task["completed"]]
    if status == "pending":
        return [task for task in tasks if not task["completed"]]
    return tasks


def parse_date(value: str) -> date:
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
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    task_date = request.form.get("date", date.today().isoformat())

    if not title:
        return redirect(url_for("index"))

    tasks = read_tasks()
    tasks.append(
        {
            "id": str(uuid4()),
            "title": title,
            "description": description,
            "date": task_date,
            "completed": False,
            "createdAt": datetime.utcnow().isoformat() + "Z",
        }
    )
    save_tasks(tasks)
    return redirect(url_for("index"))


@app.route("/toggle/<task_id>", methods=["POST"])
def toggle_task(task_id: str):
    tasks = read_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            break
    save_tasks(tasks)
    return redirect(request.referrer or url_for("index"))


@app.route("/delete/<task_id>", methods=["POST"])
def delete_task(task_id: str):
    tasks = [task for task in read_tasks() if task["id"] != task_id]
    save_tasks(tasks)
    return redirect(request.referrer or url_for("index"))


@app.route("/update/<task_id>", methods=["POST"])
def update_task(task_id: str):
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if not title:
        return redirect(url_for("index"))

    tasks = read_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = title
            task["description"] = description
            break
    save_tasks(tasks)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
