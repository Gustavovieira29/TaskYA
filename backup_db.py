# backup_db.py
import shutil
from datetime import datetime

backup_name = f"instance/tasks.db.backup-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
shutil.copy("instance/tasks.db", backup_name)
print(f"✓ Backup criado: {backup_name}")