from __init__ import create_app
import os

app = create_app()
app.secret_key = os.getenv("FLASK_SECRET_KEY")
print('test branch')
if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
