import requests

url = "http://127.0.0.1:5000/prever"

payload = {
    "bairro_group": "Manhattan",
    "latitude": 40.765,
    "longitude": -73.975,
    "room_type": "Entire home/apt",
    "quartos": 1,
    "banheiros": 1,
    #"bairro_encoded": "Harlem"
}

response = requests.post(url, json=payload)

print("Status code:", response.status_code)
print("Resposta:", response.json())


