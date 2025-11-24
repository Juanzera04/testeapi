// Substitua pela URL do seu backend no Render após o deploy
const API = "https://seu-backend.onrender.com";

// Para desenvolvimento local, comente a linha acima e descomente esta:
// const API = "http://127.0.0.1:5000";

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

        if (!response.ok) {
            throw new Error('Erro ao enviar mensagem');
        }

        document.getElementById("mensagem").value = "";
        carregar();
    } catch (error) {
        console.error("Erro:", error);
        alert("Erro ao enviar mensagem. Tente novamente.");
    }
}

async function carregar() {
    try {
        const res = await fetch(API + "/mensagens");
        
        if (!res.ok) {
            throw new Error('Erro ao carregar mensagens');
        }
        
        const dados = await res.json();

        const lista = document.getElementById("lista");
        lista.innerHTML = "";

        dados.forEach(item => {
            const div = document.createElement("div");
            div.className = "card";
            div.innerHTML = `<strong>${item.nome}</strong><p>${item.mensagem}</p>`;
            lista.appendChild(div);
        });
    } catch (error) {
        console.error("Erro ao carregar mensagens:", error);
        const lista = document.getElementById("lista");
        lista.innerHTML = "<p>Erro ao carregar mensagens</p>";
    }
}

carregar();
