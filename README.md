# 🏙️ Previsão de Preços de Imóveis do Airbnb em Nova York

Este projeto utiliza Inteligência Artificial, geolocalização e dados públicos para prever o valor de imóveis listados no Airbnb na cidade de Nova York, indicando se estão caros ou baratos em relação à média da região. Além disso, retorna a proximidade do imóvel em relação a pontos de ônibus, estações de metrô e aos principais pontos turísticos da cidade.

## 📌 Objetivo

Desenvolver uma extensão de navegador prática que, a partir das informações de um imóvel (localização, número de quartos, banheiros, etc.), que são obtidos por web scraping, retorne uma estimativa de preço e indique se o valor está acima ou abaixo do esperado para a área, com base em um modelo de Machine Learning.

🧠 Tecnologias e Ferramentas

+ Python

+ Modelos de Machine Learning

+ Flask (API para servir o modelo)

+ geopy / geodesic (cálculo de distâncias geográficas)

+ Pandas / NumPy (manipulação de dados) e extração de insights

+ JavaScript + HTML/CSS (extensão de navegador)

+ Chrome Extensions API

⚙️ Como funciona

A API recebe os seguintes dados de entrada:

+ latitude e longitude do imóvel

+ quartos e banheiros

+ room_type (tipo de acomodação)

+ bairro_group (região geral do imóvel)

A partir disso, o sistema:

Calcula as distâncias entre o imóvel e:

+ Pontos turísticos de NY (ex: Central Park, Empire State, Brooklyn Bridge, etc.)

+ Pontos de ônibus e estações de metrô mais próximas

+ Realiza o pré-processamento dos dados

+ Faz a predição de preço usando um modelo treinado com CatBoost

+ Retorna a estimativa de preço e uma avaliação do valor: caro ou barato

🌐 Extensão de Navegador

Além da API, o projeto conta com uma extensão de navegador para Google Chrome, que automatiza a análise de imóveis diretamente no site do Airbnb:

🔍 Funcionalidades:

+ Extrai automaticamente os dados do anúncio (bairro, número de quartos, latitude/longitude)

+ Envia as informações para a API

+ Exibe em tempo real se o imóvel está caro ou barato

📁 A extensão contém:

+ manifest.json: configuração da extensão

+ content.js: script que coleta dados da página

+ popup.js + popup.html: interface amigável com o usuário

+ Integração com a API local ou em nuvem

🚀 Como executar o projeto localmente

1. Clone o repositório:

   ``` git clone  https://github.com/luizcaixeta/Airbnb-price-checker```

2. Instale as dependências e execute a API
   ``` python app.py ```

3. Vá até
   ``` chrome://extensions/```

4. Ative o modo desenvolvedor

5. Clique em "Carregar sem compactação"

6. Selecione a pasta
   ```/extensao-chrome```


