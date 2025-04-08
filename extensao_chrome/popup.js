document.addEventListener("DOMContentLoaded", async () => {
    const btn = document.getElementById("avaliar");
  
    btn.addEventListener("click", () => {
      chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
        const activeTab = tabs[0];
        const url = activeTab.url;
  
        if (!url.includes("airbnb.com")) {
          alert("Este botão só funciona em páginas do Airbnb.");
          return;
        }
  
        console.log("Enviando URL:", url);
  
        const res = await fetch("http://localhost:5000/prever_por_url", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ url: url })
        });
  
        const text = await res.text();
  
        if (res.redirected || text.includes("<html")) {
          // Caso seja render_template, o texto virá como HTML completo
          document.getElementById("resultado").innerHTML = `
            <p>Resumo disponível!</p>
          `;
          document.getElementById("abrirDetalhes").style.display = "block";
          document.getElementById("detalhesLink").href = res.url || "http://localhost:5000"; // ou rota específica
          return;
        }
  
        const data = JSON.parse(text);
        console.log("Resposta JSON:", data);
  
        if (data.status === "sucesso") {
          const preco = data.preco_predito.toFixed(2);
          const resultadoDiv = document.getElementById("resultado");
          resultadoDiv.innerHTML = `
            <p><strong>Preço justo:</strong> US$ ${preco}</p>
            <p><strong>Distância até metrô:</strong> ${data.distancia_metro} m</p>
            <p><strong>Distância até ônibus:</strong> ${data.distancia_onibus} m</p>
          `;
  
          document.getElementById("abrirDetalhes").style.display = "block";
          document.getElementById("detalhesLink").href = `http://localhost:5000/prever_por_url?url=${encodeURIComponent(url)}`;
        } else {
          document.getElementById("resultado").innerHTML = `<p>Erro: ${data.mensagem}</p>`;
        }
      });
    });
  });
  