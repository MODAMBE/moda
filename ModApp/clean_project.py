import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def remove_pycache():
    print("🧠 Suppression des fichiers __pycache__ et *.pyc...")
    for root, dirs, files in os.walk(BASE_DIR):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
        for f in files:
            if f.endswith(".pyc"):
                os.remove(os.path.join(root, f))

def clean_logs():
    log_dir = BASE_DIR / "logs"
    if log_dir.exists():
        print("🗑️ Suppression des logs Django...")
        for log_file in log_dir.glob("*.log"):
            log_file.unlink()

def clean_migrations():
    print("🧩 Suppression des anciennes migrations (sauf __init__.py)...")
    for root, dirs, files in os.walk(BASE_DIR):
        if "migrations" in dirs:
            mig_dir = os.path.join(root, "migrations")
            for f in os.listdir(mig_dir):
                if f.endswith(".py") and f != "__init__.py":
                    os.remove(os.path.join(mig_dir, f))

def clean_temp():
    print("🧼 Suppression des fichiers temporaires...")
    temp_dirs = ["tmp", "temp", "media/temp", "media/cache"]
    for d in temp_dirs:
        path = BASE_DIR / d
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)

def clean_cache():
    print("🧾 Suppression des caches Django...")
    cache_dirs = [".cache", ".pytest_cache"]
    for d in cache_dirs:
        path = BASE_DIR / d
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)

if __name__ == "__main__":
    print("=== Nettoyage du projet Django en cours... ===")
    remove_pycache()
    clean_logs()
    clean_migrations()
    clean_temp()
    clean_cache()
    print("✅ Nettoyage terminé avec succès !")
