from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Caminho do banco SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mensagens.db")

# Criar tabela se não existir
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            mensagem TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Rota para adicionar mensagem
@app.post("/add")
def add_msg():
    data = request.get_json()
    nome = data.get("nome")
    mensagem = data.get("mensagem")

    if not nome or not mensagem:
        return jsonify({"erro": "Dados inválidos"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO mensagens (nome, mensagem) VALUES (?, ?)", (nome, mensagem))
    conn.commit()
    conn.close()

    return jsonify({"status": "Mensagem adicionada"})

# Rota para listar mensagens
@app.get("/mensagens")
def listar_msg():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, mensagem FROM mensagens ORDER BY id DESC")
    dados = cursor.fetchall()
    conn.close()

    lista = [{"nome": n, "mensagem": m} for n, m in dados]
    return jsonify(lista)

if __name__ == "__main__":
    app.run(debug=True)
