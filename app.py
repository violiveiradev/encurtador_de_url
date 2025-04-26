from flask import Flask, render_template, request, redirect
import hashlib
import base64

app = Flask(__name__)

# Dicionário para armazenar as URLs
urls = {}

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
    codigo = gerar_codigo(url_longa)
    urls[codigo] = url_longa
    url_encurtada = f"http://localhost:5000/{codigo}"
    return render_template("index.html", url_encurtada=url_encurtada)

# Nova rota para redirecionar
@app.route("/<codigo>")
def redirecionar(codigo):
    url_longa = urls.get(codigo)
    if url_longa:
        return redirect(url_longa)
    else:
        return "URL não encontrada!", 404

if __name__ == "__main__":
    app.run(debug=True)
