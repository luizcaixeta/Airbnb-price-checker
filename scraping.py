import requests, re

url = 'https://www.airbnb.com.br/rooms/1044485172677898752?adults=1&search_mode=regular_search&check_in=2025-07-21&check_out=2025-07-26&children=0&infants=0&pets=0&source_impression_id=p3_1744111895_P3iVlGlq2Analp4-&previous_page_section_name=1000&federated_search_id=54f43758-7a4b-4a36-ad13-e9e73d2a0ca3'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

r = requests.get(url, headers=headers)

# Latitude e longitude
lat = re.findall(r'"lat":([-0-9.]+),', r.text)[0]
lng = re.findall(r'"lng":([-0-9.]+),', r.text)[0]

# Quartos e banheiros
match_quartos = re.search(r'(\d+)\s+quarto', r.text)
match_banheiros = re.search(r'(\d+)\s+banheiro', r.text)

quartos = int(match_quartos.group(1)) if match_quartos else 0
banheiros = int(match_banheiros.group(1)) if match_banheiros else 0

# Bairro
match_bairro = re.search(r'"publicAddress":"([^"]+)"', r.text)
bairro = match_bairro.group(1).split(',')[0] if match_bairro else "Desconhecido"

# Valor da estadia
# Tenta capturar qualquer "R$" seguido de número com ponto ou vírgula
match_preco = re.search(r'<span[^>]*>\s*R\$\s*([\d\.,]+)\s*</span>', r.text)

# Fallbacks: caso não ache via <span>, tenta via JSON ou outras formas
if not match_preco:
    match_preco = re.search(r'R\$\s*([\d.,]+)\s*(?:total|Total|TOTAL)?', r.text)
if not match_preco:
    match_preco = re.search(r'"price":\s*"([^"]+)"', r.text)
if not match_preco:
    match_preco = re.search(r'totalAmount:\s*([\d.,]+)', r.text)

preco = match_preco.group(1) if match_preco else "Não encontrado"
preco_limpo = preco.replace('.', '').replace(',', '.') if isinstance(preco, str) else preco

try:
    preco_float = float(preco_limpo)
    preco_real = preco_float / 25.0  # Agora a divisão vai funcionar
except ValueError:
    preco_real = 0.0


# Avaliação - procurando pela nota média e quantidade de avaliações
# Padrão para nota (ex: 4,92)
match_nota = re.search(r'"rating":([\d.]+)', r.text) or re.search(r'(\d,\d+)\s*de\s*5', r.text)
nota = match_nota.group(1).replace(',', '.') if match_nota else "Sem avaliação"

# Quantidade de avaliações
match_qtd_avaliacoes = re.search(r'(\d+)\s*(?:avaliações|reviews|comentários)', r.text, re.IGNORECASE)
qtd_avaliacoes = match_qtd_avaliacoes.group(1) if match_qtd_avaliacoes else "0"

# Resultado
print(f"Latitude: {lat}")
print(f"Longitude: {lng}")
print(f"Quartos: {quartos}")
print(f"Banheiros: {banheiros}")
print(f"Bairro: {bairro}")
print(f"Valor da estadia: R$ {preco_real}")
print(f"Avaliação média: {nota} (de 5)")
print(f"Quantidade de avaliações: {qtd_avaliacoes}")