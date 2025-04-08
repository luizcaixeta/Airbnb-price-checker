document.addEventListener('DOMContentLoaded', function () {
  const avaliarBtn = document.getElementById('avaliar');
  const resultadoDiv = document.getElementById('resultado');
  // const abrirDetalhesDiv = document.getElementById('abrirDetalhes');
  const priceMarker = document.getElementById('priceMarker');

  // Elementos de texto
  const localizacaoSpan = document.getElementById('localizacao');
  const precoPreditoSpan = document.getElementById('precoPredito');
  const avaliacaoSpan = document.getElementById('avaliacao');
  const notaImovelSpan = document.getElementById('notaImovel');
  const metroSpan = document.getElementById('metroProximo');
  const onibusSpan = document.getElementById('onibusProximo');
  // const detalhesLink = document.getElementById('detalhesLink');
;

  avaliarBtn.addEventListener('click', function () {
    // Mostra estado de carregamento
    avaliarBtn.innerHTML = '<span class="loading"></span> Analisando...';
    avaliarBtn.disabled = true;

    // Obtém a URL atual da página do Airbnb
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      const currentTab = tabs[0];
      if (!currentTab.url.includes('airbnb')) {
        mostrarErro("Esta não é uma página do Airbnb");
        return;
      }

      // Envia a URL para o backend
      fetch('http://localhost:5000/prever_por_url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: currentTab.url }),
      })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'erro') {
            mostrarErro(data.mensagem);
            return;
          }

          processarResposta(data, currentTab.url);
        })
        .catch(error => {
          console.error('Erro:', error);
          mostrarErro("Erro na conexão com o servidor");
        });
    });
  });

  function processarResposta(data, url) {
    const precoAtual = parseFloat(data.preco_atual) || 0;
    const precoPredito = parseFloat(data.preco_predito) || 0;
    const nota = data.nota || "Sem avaliação";
    const bairroGroup = data.bairro_group || "Desconhecido";

    const diferenca = ((precoAtual - precoPredito) / precoPredito) * 100;
    const diferencaAbs = Math.abs(diferenca);

    const metro = data.distancia_metro;
    const onibus = data.distancia_onibus;

    const distancias = data.distancias_turisticos;

    const emojisTuristicos = {
      'Central Park': '🌳',
      'Times Square': '🎆',
      'Empire State Building': '🏙️',
      'Museu da arte moderna': '🖼️',
      'Museu da cidade de NY': '🏛️',
      'Museu memorial': '🕊️',
      'One World Trade Center': '🗽',
      'Centro cívico': '🏢',
      'Lincoln Center for the Performing Arts': '🎭',
      'Brooklyn Bridge': '🌉',
      'Brooklyn Bridge Park': '🏞️',
      'Brooklyn Museum': '🖼️',
      'McCarren Park': '🌲',
      'East River': '🌊'
    };
    
    const pontosProximos = Object.entries(distancias)
      .filter(([nome, distancia]) => distancia < 5000)
      .map(([nome, distancia]) => {
        const nomeLimpo = nome.replace('distancia_', '').replace(/_/g, ' ');
        const nomeFormatado = nomeLimpo.replace(/\b\w/g, l => l.toUpperCase());
        const emoji = emojisTuristicos[nomeFormatado] || '📍';
        const distanciaKm = (distancia / 1000).toFixed(2);
        return `<li>${emoji} ${nomeFormatado}: ${distanciaKm} km</li>`;
      });
    
    document.getElementById('pontos-turisticos').innerHTML = pontosProximos.length > 0
      ? `<h4>Pontos turísticos próximos (menos de 5km):</h4><ul>${pontosProximos.join('')}</ul>`
      : `<h4>Nenhum ponto turístico a menos de 5km</h4>`;
    

    if (metro !== undefined) {
      metroSpan.textContent = `${metro} metros`;
    } else {
      metroSpan.textContent = "Não encontrado";
    }
    
    if (onibus !== undefined) {
      onibusSpan.textContent = `${onibus} metros`;
    } else {
      onibusSpan.textContent = "Não encontrado";
    }
    

    let avaliacao, classeAvaliacao, detalhes;

    if (diferenca < -20) {
      avaliacao = "Ótimo negócio!";
      classeAvaliacao = "good";
      detalhes = `Preço ${diferencaAbs.toFixed(1)}% abaixo do valor previsto para esta localização.`;
    } else if (diferenca >= -20 && diferenca <= 20) {
      avaliacao = "Preço justo";
      classeAvaliacao = "average";
      detalhes = `Preço dentro da faixa esperada (${diferenca > 0 ? 'acima' : 'abaixo'} ${diferencaAbs.toFixed(1)}%).`;
    } else {
      avaliacao = "Acima do esperado";
      classeAvaliacao = "bad";
      detalhes = `Preço ${diferencaAbs.toFixed(1)}% acima do valor previsto para esta localização.`;
    }

    const posicao = Math.min(100, Math.max(0, 50 + (diferenca / 2)));
    priceMarker.style.left = `${posicao}%`;

    // Atualiza a interface com os dados reais
    localizacaoSpan.textContent = bairroGroup;
    precoPreditoSpan.textContent = `$ ${precoPredito.toFixed(2)}`;
    avaliacaoSpan.textContent = avaliacao;
    avaliacaoSpan.className = `rating ${classeAvaliacao}`;
    notaImovelSpan.textContent = nota;
    // detalhesLink.href = `http://localhost:5000/prever_por_url?url=${encodeURIComponent(url)}`;

    resultadoDiv.style.display = 'block';
    // abrirDetalhesDiv.style.display = 'block';

    avaliarBtn.innerHTML = 'Analisar novamente';
    avaliarBtn.disabled = false;
  }

  function mostrarErro(mensagem) {
    resultadoDiv.innerHTML = `<p style="color:red;">${mensagem}</p>`;
    resultadoDiv.style.display = 'block';
  
    avaliarBtn.textContent = 'Tentar novamente';
    avaliarBtn.disabled = false;
  }
});
