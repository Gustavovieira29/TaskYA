"""Sistema de logging e auditoria para operações do banco de dados."""

import logging
from datetime import datetime
from pathlib import Path

# Criar diretório de logs se não existir
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configurar logging
log_file = LOG_DIR / f"operations_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()  # Também exibe no console
    ]
)

logger = logging.getLogger(__name__)


def log_create(task_id: str, title: str, date_str: str) -> None:
    """Registra criação de tarefa."""
    logger.info(f"CREATE - ID: {task_id} | Título: {title} | Data: {date_str}")


def log_update(task_id: str, field: str, old_value: str, new_value: str) -> None:
    """Registra atualização de tarefa."""
    logger.info(f"UPDATE - ID: {task_id} | Campo: {field} | Anterior: {old_value} → Novo: {new_value}")


def log_delete(task_id: str, title: str) -> None:
    """Registra exclusão de tarefa."""
    logger.warning(f"DELETE - ID: {task_id} | Título: {title}")


def log_toggle(task_id: str, title: str, new_status: bool) -> None:
    """Registra alteração de status."""
    status = "✓ Concluída" if new_status else "○ Pendente"
    logger.info(f"TOGGLE - ID: {task_id} | Título: {title} | Novo Status: {status}")


def log_error(operation: str, error: Exception) -> None:
    """Registra erros."""
    logger.error(f"ERRO em {operation}: {str(error)}")
