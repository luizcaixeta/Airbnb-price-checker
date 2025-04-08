import requests, re

url = 'https://www.airbnb.com.br/rooms/54068618?search_mode=regular_search&adults=1&category_tag=Tag%3A8678&check_in=2025-07-20&check_out=2025-07-25&children=0&infants=0&pets=0&photo_id=1312770556&source_impression_id=p3_1744059458_P3OM-c3oCep2ZxNN&previous_page_section_name=1000&federated_search_id=a5b9c7fe-921e-4d4b-b12b-286efc3bc27f'  # troque pelo link do anúncio

r = requests.get(url)

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

# Resultado
print(f"Latitude: {lat}")
print(f"Longitude: {lng}")
print(f"Quartos: {quartos}")
print(f"Banheiros: {banheiros}")
print(f"Bairro: {bairro}")
