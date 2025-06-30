from __init__ import create_app
import os

app = create_app()
app.secret_key = os.getenv("FLASK_SECRET_KEY")
