from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# -------------------------------------------
# CONFIGURAÇÃO DO BANCO (Com suas credenciais)
# -------------------------------------------
def get_db_connection():
    # No Render, usa DATABASE_URL automaticamente
    # Para desenvolvimento, use a URL externa que você recebeu
    database_url = os.environ.get('DATABASE_URL', 'postgresql://admin:dMoMPubwqoeu2nDL9ufmnMsld8sMMXnu@dpg-d4i49r8gjchc73dkstu0-a.oregon-postgres.render.com/mensagens_db_txyh')
    
    try:
        conn = psycopg2.connect(
            database_url,
            sslmode='require'
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar com o banco: {e}")
        raise

# -------------------------------------------
# INICIAR BANCO (PostgreSQL)
# -------------------------------------------
def init_db():
    try:
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
        print("Tabela 'mensagens' verificada/criada com sucesso!")
        conn.close()
    except Exception as e:
        print(f"Erro ao inicializar banco: {e}")

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
        return jsonify({"status": "unhealthy", "database": "disconnected"}), 500

# -------------------------------------------
# RODAR API
# -------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
