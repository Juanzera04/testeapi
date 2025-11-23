const API = "http://127.0.0.1:5000"; // depois troque pela URL do Render

async function enviar() {
    const nome = document.getElementById("nome").value;
    const mensagem = document.getElementById("mensagem").value;

    if (!nome || !mensagem) {
        alert("Preencha tudo");
        return;
    }

    await fetch(API + "/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome, mensagem })
    });

    document.getElementById("mensagem").value = "";
    carregar();
}

async function carregar() {
    const res = await fetch(API + "/mensagens");
    const dados = await res.json();

    const lista = document.getElementById("lista");
    lista.innerHTML = "";

    dados.forEach(item => {
        const div = document.createElement("div");
        div.className = "card";
        div.innerHTML = `<strong>${item.nome}</strong><p>${item.mensagem}</p>`;
        lista.appendChild(div);
    });
}

carregar();
