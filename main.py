"""
Point d'entrée principal pour lancer l'application dashboard.

Ce script importe et exécute l'application Dash définie dans
le package `src.dashboard`.

Executez main.py pour lancer l'application
"""

from src.dashboard.app import app, server   # 1. Importe l'app Dash
from src.dashboard import layout          # 2. Importe le layout (l'attache à l'app)
from src.dashboard import callbacks       # 3. Importe les callbacks (les lie à l'app)

# --- Lancement du serveur ---
if __name__ == '__main__':
    # Lance le serveur en mode debug
    app.run(debug=True)