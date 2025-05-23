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

        # Cria a tabela 'urls' (se não existir)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                codigo TEXT PRIMARY KEY,
                url_longa TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS acessos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT,
                data_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (codigo) REFERENCES urls(codigo)
            )
        ''')
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

    # Código personalizado
    codigo_personalizado = request.form.get("codigo_personalizado", "").strip()

    # Validação
    if not validators.url(url_longa):
        error =  "URL inválida! Certifique-se de incluir 'http://' ou 'https://'."
    else:
        error = None

    db = get_db()
    cursor = db.cursor()

    # Se houver código personalizado, usa ele (após validar)
    if codigo_personalizado:
        if not codigo_personalizado.isalnum():
            error = "Código personalizado inválido! Só pode conter letras e números."
            return render_template("index.html", error=error)
        
        cursor.execute("SELECT codigo FROM urls WHERE codigo = ?", (codigo_personalizado,))
        if cursor.fetchone():
            error = "Este código já está em uso! Escolha outro."
            return render_template("index.html", error=error)
        
        codigo = codigo_personalizado
    else:
        codigo = gerar_codigo(url_longa)

    # Insere no banco de dados
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

    # Registra o acesso
    cursor.execute("INSERT INTO acessos (codigo) VALUES (?)", (codigo,))
    db.commit()

    # Redireciona
    cursor.execute("SELECT url_longa FROM urls WHERE codigo = ?", (codigo,))
    resultado = cursor.fetchone()

    if resultado:
        return redirect(resultado["url_longa"])
    else:
        return "URL não encontrada!", 404
    
@app.route("/stats/<codigo>")
def stats(codigo):
    db = get_db()
    cursor = db.cursor()

    # Contagem de acessos
    cursor.execute("SELECT COUNT(*) AS total FROM acessos WHERE codigo = ?", (codigo,))
    total_acessos = cursor.fetchone()["total"]

    # URL original
    cursor.execute("SELECT url_longa FROM urls WHERE codigo = ?", (codigo,))
    url = cursor.fetchone()["url_longa"]

    return render_template("stats.html", codigo=codigo, url=url, total_acessos=total_acessos)

@app.route("/table")
def urls_table():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT 
            urls.codigo, 
            urls.url_longa, 
            COUNT(acessos.id) AS total_acessos
        FROM urls
        LEFT JOIN acessos ON urls.codigo = acessos.codigo
        GROUP BY urls.codigo
        ORDER BY urls.codigo
    ''')
    
    urls = cursor.fetchall()
    return render_template("table.html", urls=urls)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)