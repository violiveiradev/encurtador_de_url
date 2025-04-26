from flask import Flask, render_template, request, redirect
import random

app = Flask(__name__)

# Dicionário para armazenar as URLs
urls = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/encurtar", methods=["POST"])
def encurtar():
    url_longa = request.form["url_longa"]
    codigo = str(random.randint(1000, 9999))
    urls[codigo] = url_longa
    url_encurtada = f"http://localhost:5000/{codigo}"
    return render_template("index.html", url_encurtada=url_encurtada)

# Nova rota para redirecionar
@app.route("/<codigo>")
def redirecionar(codigo):
    url_longa = urls.get(codigo)
    print(urls)
    if url_longa:
        return redirect(url_longa)
    else:
        return "URL não encontrada!", 404

if __name__ == "__main__":
    app.run(debug=True)
