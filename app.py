from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from sklearn.neighbors import KDTree
import requests
import re

app = Flask(__name__)
CORS(app)

# Carrega o modelo e o scaler
melhor_modelo = joblib.load("melhor_modelo_CatBoostRegressor.pkl")
scaler = joblib.load("scaler.pkl")

# Configurações e constantes
BAIRRO_GROUP_MAPPING = {
    'Manhattan': 1, 'Brooklyn': 2, 'Staten Island': 3, 'Queens': 4, 'Bronx': 5
}


ROOM_TYPES_MAPPING = {
    'Entire home/apt': 1,
    'Private room': 2,
    'Shared room': 3
}

def limpar_coordenadas(df, lat_col, lon_col):

    print("Antes:", df.shape)
    print("Colunas disponíveis:", df.columns)

    # Corrigir formatação: trocar ponto por nada, depois adicionar ponto decimal no lugar certo (se necessário)
    df[lat_col] = df[lat_col].astype(str).str.replace('.', '', regex=False)
    df[lat_col] = df[lat_col].str[:2] + '.' + df[lat_col].str[2:]
    df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')

    df[lon_col] = df[lon_col].astype(str).str.replace('.', '', regex=False)
    df[lon_col] = df[lon_col].str[:3] + '.' + df[lon_col].str[3:]
    df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')

    df = df.dropna(subset=[lat_col, lon_col])
    print("Depois:", df.shape)
    return df

# Carrega e prepara os dados geográficos
def load_geodata():

    estacoes = pd.read_csv("dados/MTA_Subway_Entrances_and_Exits__2024_20250129.csv")
    ponto_onibus = pd.read_csv("dados/Bus_Stop_Shelter_20250201 - Bus_Stop_Shelter_20250201.csv")
    centroides = pd.read_csv("dados/centroides_bairro_group.csv")

    estacoes = estacoes.rename(columns={"Entrance Latitude": "Latitude", 
                                        "Entrance Longitude": "Longitude"})

    estacoes = limpar_coordenadas(estacoes, "Latitude", "Longitude")

    ponto_onibus = ponto_onibus.rename(columns={
        "Latitude": "Latitude_temp",
        "Longitude": "Longitude_temp"
    }).rename(columns={
        "Latitude_temp": "Latitude",
        "Longitude_temp": "Longitude"
    })

    ponto_onibus = limpar_coordenadas(ponto_onibus, "Latitude", "Longitude")

    return {
        'tree_metro': KDTree(estacoes[["Latitude", "Longitude"]].values),
        'tree_onibus': KDTree(ponto_onibus[["Latitude", "Longitude"]].values),
        'centroides': centroides,
        'estacoes': estacoes,
        'ponto_onibus': ponto_onibus
    }

geodata = load_geodata()

#Funções auxiliares


from geopy.distance import geodesic

def calcular_distancia_kdtree(lat, lon,tree, pontos):

    distancias, indices = tree.query([[lat, lon]], k = 1)

    idx = indices[0][0]

    ponto_lat = pontos.iloc[idx]["Latitude"]
    ponto_lon = pontos.iloc[idx]["Longitude"]
    distancia = geodesic((lat, lon), (ponto_lat, ponto_lon)).meters

    return distancia, (ponto_lat, ponto_lon)


def inferir_bairro_group(lat, lon):

    menor_distancia = float('inf')
    bairro_group_inferido = None

    for _, row in geodata['centroides'].iterrows():
        centroide_lat = row['lat']
        centroide_lon = row['lng']
        distancia = geodesic((lat, lon), (centroide_lat, centroide_lon)).meters
        
        if distancia < menor_distancia:
            menor_distancia = distancia
            bairro_group_inferido = row['bairro_group']

    return bairro_group_inferido

def validate_input(data):
    errors = []

    # Validar latitude e longitude
    if not isinstance(data.get("latitude"), float) or not (-90 <= data["latitude"] <= 90):
        errors.append("Latitude deve ser float entre -90 e 90")
    
    if not isinstance(data.get("longitude"), float) or not (-180 <= data["longitude"] <= 180):
        errors.append("Longitude deve ser float entre -180 e 180")

    # Validar room_type
    if not isinstance(data.get("room_type"), int) or data["room_type"] not in ROOM_TYPES_MAPPING.values():
        errors.append(f"room_type inválido. Esperado um dos valores: {list(ROOM_TYPES_MAPPING.values())}")

    # Validar quartos e banheiros
    for field in ['quartos', 'banheiros']:
        value = data.get(field)
        if not isinstance(value, int) or value < 1:
            errors.append(f"{field} deve ser inteiro maior ou igual a 1")
    
    return errors

def preprocess_user_data(user_data):

    df_user = pd.DataFrame([user_data])
    
    df_user['room_type'] = df_user['room_type'].map(ROOM_TYPES_MAPPING).fillna(0)

    # Tratar bairro_group
    if 'bairro_group' not in df_user.columns or pd.isna(df_user['bairro_group'].iloc[0]):
        bairro_inferido = inferir_bairro_group(user_data['latitude'], user_data['longitude'])
        df_user['bairro_group'] = bairro_inferido
    
    if df_user['bairro_group'].dtype == object:
        df_user['bairro_group'] = df_user['bairro_group'].map(BAIRRO_GROUP_MAPPING).fillna(0)


    print("Bairro group final: ", df_user['bairro_group'].iloc[0])

    #Calcular distâncias
    lat, lon = user_data['latitude'], user_data['longitude']
    
    #adiciona distância até a estação de metrô mais próxima
    # Distância metrô
    dist_metro, parada_metro = calcular_distancia_kdtree(
        lat, lon, geodata['tree_metro'], geodata['estacoes'][["Latitude", "Longitude"]]
    )
    df_user["distancia_metro"] = dist_metro

    print(f"Distância até estação de metrô mais próxima: {dist_metro:.3f} m")

    #adiciona distância até o ponto de ônibus mais próximo
    dist_onibus, parada_onibus = calcular_distancia_kdtree(
        lat, lon, geodata['tree_onibus'], geodata['ponto_onibus'][["Latitude", "Longitude"]]
    )
    df_user["distancia_onibus"] = dist_onibus
    print(f"Distância até ponto de ônibus mais próximo: {dist_onibus:.3f} m")

    # Calcula distância aos pontos turísticos
    for ponto in pontos_turisticos:
        nome = ponto["nome"]
        distancia = geodesic((lat, lon), (ponto["latitude"], ponto["longitude"])).meters
        df_user[f"distancia_{nome}"] = distancia
        print(f"Distância até {nome}: {distancia:.3f} m")

    # Ajusta colunas
    expected_columns = [
        'bairro_group', 'latitude', 'longitude', 'room_type', 
        'distancia_metro', 'distancia_onibus', 'quartos', 'banheiros',
        'distancia_Central Park', 'distancia_Times Square', 'distancia_Empire State Building',
        'distancia_Museu da arte moderna', 'distancia_Museu da cidade de NY', 'distancia_Museu memorial',
        'distancia_One World Trade Center', 'distancia_Centro cívico', 'distancia_Lincoln Center for the Performing Arts',
        'distancia_Brooklyn Bridge', 'distancia_Brooklyn Bridge Park', 'distancia_Brooklyn Museum',
        'distancia_McCarren Park', 'distancia_East River'#, 'bairro_encoded'
    ]

    df_user_final = df_user.reindex(columns=expected_columns, fill_value=0)

    print("=== Dados prontos para o modelo ===")
    print(df_user_final.dtypes)
    print(df_user_final)

    return df_user_final, dist_metro, dist_onibus, parada_metro, parada_onibus
# Lista de pontos turísticos
pontos_turisticos = [
    {"nome": "Central Park", "latitude": 40.785091, "longitude": -73.968285},
    {"nome": "Times Square", "latitude": 40.758896, "longitude": -73.985130},
    {"nome": "Empire State Building", "latitude": 40.748817, "longitude": -73.985428},
    {"nome": "Museu da arte moderna", "latitude": 40.763448, "longitude": -73.977157},
    {"nome": "Museu da cidade de NY", "latitude": 40.79303, "longitude": -73.95476},
    {"nome": "Museu memorial", "latitude": 40.71227, "longitude": -74.01511},
    {"nome": "One World Trade Center", "latitude": 40.71249, "longitude": -74.01198},
    {"nome": "Centro cívico", "latitude": 40.71412, "longitude": -74.00206},
    {"nome": "Lincoln Center for the Performing Arts", "latitude": 40.77324, "longitude": -73.98667},
    {"nome": "Brooklyn Bridge", "latitude": 40.70627, "longitude": -73.99676},
    {"nome": "Brooklyn Bridge Park", "latitude": 40.70240, "longitude": -73.99573},
    {"nome": "Brooklyn Museum", "latitude": 40.67130, "longitude": -73.96357},
    {"nome": "McCarren Park", "latitude": 40.72100, "longitude": -73.95159},
    {"nome": "East River", "latitude": 40.72506, "longitude": -73.96744}
]

@app.route('/prever_por_url', methods=['GET', 'POST'])
def prever_por_url():
    try:
        print("\n=== Requisição recebida ===")

        # Suporte a GET (para link no popup) e POST (para fetch do JS)
        if request.method == 'POST':
            print("Dados recebidos (POST):", request.json)
            dados = request.json
            url = dados.get('url')
        else:  # GET
            url = request.args.get('url')
            print("Dados recebidos (GET):", url)

        if not url:
            print("URL ausente!")
            return jsonify({
                "status": "erro", 
                "mensagem": "URL ausente"
            }), 400

        r = requests.get(url)
        print("Scraping feito com sucesso!")

        lat = float(re.findall(r'"lat":([-0-9.]+),', r.text)[0])
        lng = float(re.findall(r'"lng":([-0-9.]+),', r.text)[0])
        print(f"Latitude: {lat}, Longitude: {lng}")

        match_quartos = re.search(r'(\d+)\s+quarto', r.text)
        match_banheiros = re.search(r'(\d+)\s+banheiro', r.text)
        quartos = int(match_quartos.group(1)) if match_quartos else 1
        banheiros = int(match_banheiros.group(1)) if match_banheiros else 1
        print(f"Quartos: {quartos}, Banheiros: {banheiros}")

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
        
        print(f"Preço: {preco_real}")

        match_nota = re.search(r'"rating":([\d.]+)', r.text) or re.search(r'(\d,\d+)\s*de\s*5', r.text)
        nota = match_nota.group(1).replace(',', '.') if match_nota else "Sem avaliação"

        print(f"Avaliação: {nota}")

        match_bairro = re.search(r'"publicAddress":"([^"]+)"', r.text)
        bairro = "Desconhecido"
        if match_bairro:
            bairro = match_bairro.group(1).split(',')[0]
        print(f"Bairro extraído: {bairro}")

        if bairro == "Desconhecido":
            bairro_group = inferir_bairro_group(lat, lng)
            print(f"Bairro inferido com base em coordenadas: {bairro_group}")
        else:
            bairro_group = None

        user_data = {
            "latitude": lat,
            "longitude": lng,
            "room_type": 1,
            "quartos": quartos,
            "banheiros": banheiros,
            "bairro_group": bairro_group
        }

        print("User data:", user_data)


        validation_errors = validate_input(user_data)
        if validation_errors:
            return jsonify({
                "status": "erro", 
                "mensagem": "dados inválidos", 
                "erros": validation_errors
            }), 400

        df_processed, distancia_metro, distancia_onibus, parada_metro, parada_onibus = preprocess_user_data(user_data)
        print("Processed DF:", df_processed.head())

        df_scaled = scaler.transform(df_processed)
        predicted_price = round(float(melhor_modelo.predict(df_scaled)[0]), 2)
        print("Preço previsto:", predicted_price)

        # Resposta para popup.js (resumo em JSON)
        if request.method == 'POST':
            return jsonify({
                "status": "sucesso",
                "preco_predito": predicted_price,
                "preco_atual": preco_real,
                "nota": nota,
                "bairro_group": bairro_group,
                "distancia_metro": round(distancia_metro, 1),
                "distancia_onibus": round(distancia_onibus, 1),
                "pontos_turisticos": [p["nome"] for p in pontos_turisticos],
                "pontos_turisticos_coord": pontos_turisticos,
                "distancias_turisticos": {
                    f"distancia_{p['nome']}": round(df_processed.iloc[0][f"distancia_{p['nome']}"], 1)
                    for p in pontos_turisticos
                },
                "latitude": lat,
                "longitude": lng
            })

        # Resposta para link (render_template com todos os detalhes)
        return render_template(
            "result.html",
            predicted_price=predicted_price,
            distancia_metro= float(round(distancia_metro, 1)),
            distancia_onibus= float(round(distancia_onibus, 1)),
            #pontos_turisticos=[p["nome"] for p in pontos_turisticos],
            #pontos_turisticos_coord=pontos_turisticos,
            latitude=lat,
            longitude=lng
            #latitude_metro=parada_metro[0] if parada_metro else None,
            #longitude_metro=parada_metro[1] if parada_metro else None,
            #latitude_onibus=parada_onibus[0] if parada_onibus else None,
            #longitude_onibus=parada_onibus[1] if parada_onibus else None
        )

    except Exception as e:
        print("Erro durante o processo:", str(e))
        return jsonify({
            "status": "erro", 
            "mensagem": "Erro no scraping ou previsão", 
            "detalhes": str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
