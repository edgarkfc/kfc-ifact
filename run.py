# C:\kfc-ifact\run.py (nuevo archivo en la raíz)
from server.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)