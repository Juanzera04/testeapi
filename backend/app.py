from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
import urllib.parse as urlparse

app = Flask(__name__)
CORS(app)

# -------------------------------------------
# CONFIGURAÇÃO DO BANCO (PostgreSQL no Render)
# -------------------------------------------
def get_db_connection():
    # No Render, usa DATABASE_URL; localmente pode usar variável de ambiente
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Parse da URL do PostgreSQL
        url = urlparse.urlparse(database_url)
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port
        
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            sslmode='require'
        )
    else:
        # Fallback para desenvolvimento local
        conn = psycopg2.connect(
            dbname='mensagens_db',
            user='postgres',
            password='sua_senha_local',
            host='localhost',
            port='5432'
        )
    
    return conn

# -------------------------------------------
# INICIAR BANCO (PostgreSQL)
# -------------------------------------------
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print("✅ Tabela 'mensagens' verificada/criada com sucesso!")

init_db()

# -------------------------------------------
# ROTA RAIZ (TESTE)
# -------------------------------------------
@app.get("/")
def home():
    return jsonify({
        "status": "API rodando com PostgreSQL no Render!",
        "database": "Conectado ao PostgreSQL",
        "rotas": ["/add", "/mensagens"]
    })

# -------------------------------------------
# ADICIONAR MENSAGEM
# -------------------------------------------
@app.post("/add")
def add_msg():
    data = request.get_json()

    nome = data.get("nome")
    mensagem = data.get("mensagem")

    if not nome or not mensagem:
        return jsonify({"erro": "Nome e mensagem são obrigatórios"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mensagens (nome, mensagem) VALUES (%s, %s)",
            (nome, mensagem)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "Mensagem adicionada com sucesso!"})
    except Exception as e:
        return jsonify({"erro": f"Erro no servidor: {str(e)}"}), 500

# -------------------------------------------
# LISTAR MENSAGENS
# -------------------------------------------
@app.get("/mensagens")
def listar_msg():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, mensagem FROM mensagens ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        dados = [{"nome": r[0], "mensagem": r[1]} for r in rows]
        return jsonify({
            "total": len(dados),
            "mensagens": dados
        })
    except Exception as e:
        return jsonify({"erro": f"Erro ao carregar mensagens: {str(e)}"}), 500

# -------------------------------------------
# HEALTH CHECK (Importante para o Render)
# -------------------------------------------
@app.get("/health")
def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "database": "disconnected", "erro": str(e)}), 500

# -------------------------------------------
# RODAR API
# -------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
