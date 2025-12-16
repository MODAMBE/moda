import os
import sys
import webbrowser

# Définir le settings Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ModApp.settings")

from django.core.management import execute_from_command_line

# Ouvre automatiquement le navigateur sur la page d'accueil
webbrowser.open("http://127.0.0.1:8000/")  # Localhost pour test

# Lance le serveur Django local
execute_from_command_line([sys.argv[0], "runserver", "127.0.0.1:8000"])
