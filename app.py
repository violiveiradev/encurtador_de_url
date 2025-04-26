from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Dicionário para armazenar as URLs
urls = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/encurtar", methods=["POST"])
def encurtar():
    url_longa = request.form["url_longa"]
    # Gerar um código curto (por enquanto, usaremos um número aleatório)
    import random
    codigo = str(random.randint(1000, 9999))
    return f"URL encurtada: http://localhost:5000/{codigo}"

if __name__ == "__main__":
    app.run(debug=True)
