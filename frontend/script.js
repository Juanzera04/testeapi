// Substitua pela URL real do seu backend
const API = "https://meu-backend1.onrender.com";

async function enviar() {
    const nome = document.getElementById("nome").value;
    const mensagem = document.getElementById("mensagem").value;

    if (!nome || !mensagem) {
        alert("Preencha tudo");
        return;
    }

    try {
        const response = await fetch(API + "/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome, mensagem })
        });

        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.erro || 'Erro ao enviar mensagem');
        }

        alert("Mensagem enviada com sucesso!");
        document.getElementById("mensagem").value = "";
        carregar();
    } catch (error) {
        console.error("Erro:", error);
        alert("Erro ao enviar mensagem: " + error.message);
    }
}

async function carregar() {
    try {
        const res = await fetch(API + "/mensagens");
        
        if (!res.ok) {
            throw new Error('Erro ao carregar mensagens');
        }
        
        const data = await res.json();
        const dados = data.mensagens || data;

        const lista = document.getElementById("lista");
        lista.innerHTML = "";

        if (dados.length === 0) {
            lista.innerHTML = "<p>Nenhuma mensagem ainda. Seja o primeiro a escrever!</p>";
            return;
        }

        dados.forEach(item => {
            const div = document.createElement("div");
            div.className = "card";
            div.innerHTML = `<strong>${item.nome}</strong><p>${item.mensagem}</p>`;
            lista.appendChild(div);
        });
    } catch (error) {
        console.error("Erro ao carregar mensagens:", error);
        const lista = document.getElementById("lista");
        lista.innerHTML = "<p>Erro ao carregar mensagens. Tente recarregar a página.</p>";
    }
}

// Carrega as mensagens quando a página abre
document.addEventListener('DOMContentLoaded', carregar);
