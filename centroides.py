import pandas as pd
from geopy.distance import geodesic

#carrega o dataset original
df = pd.read_csv('dados/Airbnb_NY_data.csv')  

#agrupa por bairro_group e calcula a média de latitude e longitude
centroides_group_df = df.groupby('bairro_group')[['latitude', 'longitude']].mean().reset_index()
centroides_group_df.rename(columns={'latitude': 'lat', 'longitude': 'lng'}, inplace=True)

#agrupa por bairro e calcula a média de latitude 
centroides_df = df.groupby('bairro')[['latitude', 'longitude']].mean().reset_index()
centroides_df.rename(columns={'latitude': 'lat', 'longitude': 'lng'}, inplace=True)

#salva os centroides para reutilização
centroides_group_df.to_csv('centroides_bairro_group.csv', index=False)
centroides_df.to_csv('centroides_bairro.csv', index=False)
print("Centroides salvos em 'centroides_bairro_group.csv' e 'centroides_bairro.csv.")

#função para estimar o bairro_group com base em coordenadas 
def estimar_bairro_group(lat, lng, centroides):
    ponto = (float(lat), float(lng))
    distancias = centroides.apply(
        lambda row: geodesic(ponto, (row['lat'], row['lng'])).meters, axis=1
    )
    idx = distancias.idxmin()
    return centroides.loc[idx, 'bairro_group']

#função para estimar o bairro com base em coordenadas 
def estimar_bairro_group(lat, lng, centroides):
    ponto = (float(lat), float(lng))
    distancias = centroides.apply(
        lambda row: geodesic(ponto, (row['lat'], row['lng'])).meters, axis=1
    )
    idx = distancias.idxmin()
    return centroides.loc[idx, 'bairro']
