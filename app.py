from flask import Flask, render_template, request, redirect, g
import hashlib
import base64
import sqlite3
import validators

app = Flask(__name__)

# Configuração do banco de dados
DATABASE = "db.sqlite3"

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            url_longa TEXT NOT NULL
        )''')
        db.commit()
# Inicializa o banco de dados ao iniciar o app
init_db()	


def gerar_codigo(url_longa):
    # Cria um hash usando SHA-256 e converte para base64 (mais curto)
    hash_bytes = hashlib.sha256(url_longa.encode()).digest()
    codigo = base64.urlsafe_b64encode(hash_bytes).decode()[:6]
    return codigo

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/encurtar", methods=["POST"])
def encurtar():
    url_longa = request.form["url_longa"]

    # Validação
    if not validators.url(url_longa):
        error =  "URL inválida! Certifique-se de incluir 'http://' ou 'https://'."
    else:
        error = None
    
    codigo = gerar_codigo(url_longa)

    db = get_db()
    cursor = db.cursor()
    
    # Verifica se a URL já existe no banco de dados
    cursor.execute("SELECT codigo FROM urls WHERE url_longa = ?", (url_longa,))
    resultado = cursor.fetchone()
    
    if resultado:
        codigo = resultado["codigo"]
    else:
        cursor.execute("INSERT INTO urls (codigo, url_longa) VALUES (?, ?)", (codigo, url_longa))
        db.commit()

    context = {
        "url_encurtada": f"http://localhost:5000/{codigo}",
        "error": error
    }
    return render_template("index.html", **context)

# Nova rota para redirecionar
@app.route("/<codigo>")
def redirecionar(codigo):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT url_longa FROM urls WHERE codigo = ?", (codigo,))
    resultado = cursor.fetchone()

    if resultado:
        return redirect(resultado["url_longa"])
    else:
        return "URL não encontrada!", 404

if __name__ == "__main__":
    app.run(debug=True)
