from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncpg
import os
import asyncio

app = Flask(__name__)
CORS(app)

# -------------------------------------------
# CONFIGURAÇÃO DO BANCO (Com asyncpg)
# -------------------------------------------
async def get_db_connection():
    database_url = os.environ.get('DATABASE_URL', 'postgresql://admin:dMoMPubwqoeu2nDL9ufmnMsld8sMMXnu@dpg-d4i49r8gjchc73dkstu0-a.oregon-postgres.render.com/mensagens_db_txyh')
    return await asyncpg.connect(database_url)

# -------------------------------------------
# INICIAR BANCO (PostgreSQL)
# -------------------------------------------
async def init_db():
    try:
        conn = await get_db_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS mensagens (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await conn.close()
        print("Tabela 'mensagens' verificada/criada com sucesso!")
    except Exception as e:
        print(f"Erro ao inicializar banco: {e}")

# Executar a inicialização na startup
import atexit
atexit.register(lambda: asyncio.run(init_db()))

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
async def add_msg():
    data = request.get_json()

    nome = data.get("nome")
    mensagem = data.get("mensagem")

    if not nome or not mensagem:
        return jsonify({"erro": "Nome e mensagem são obrigatórios"}), 400

    try:
        conn = await get_db_connection()
        await conn.execute(
            "INSERT INTO mensagens (nome, mensagem) VALUES ($1, $2)",
            nome, mensagem
        )
        await conn.close()
        return jsonify({"status": "Mensagem adicionada com sucesso!"})
    except Exception as e:
        return jsonify({"erro": f"Erro no servidor: {str(e)}"}), 500

# -------------------------------------------
# LISTAR MENSAGENS
# -------------------------------------------
@app.get("/mensagens")
async def listar_msg():
    try:
        conn = await get_db_connection()
        rows = await conn.fetch("SELECT nome, mensagem FROM mensagens ORDER BY id DESC")
        await conn.close()

        dados = [{"nome": r['nome'], "mensagem": r['mensagem']} for r in rows]
        return jsonify({
            "total": len(dados),
            "mensagens": dados
        })
    except Exception as e:
        return jsonify({"erro": f"Erro ao carregar mensagens: {str(e)}"}), 500

# -------------------------------------------
# HEALTH CHECK
# -------------------------------------------
@app.get("/health")
async def health_check():
    try:
        conn = await get_db_connection()
        await conn.fetch("SELECT 1")
        await conn.close()
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "database": "disconnected"}), 500

# -------------------------------------------
# RODAR API
# -------------------------------------------
if __name__ == "__main__":
    # Inicializar o banco na startup
    asyncio.run(init_db())
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
