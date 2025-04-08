// Inicializa o Mapa
const map = L.map('map').setView([propertyLocation.lat, propertyLocation.lng], 15);

// Adiciona base map (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

// Ícones Customizados
const propertyIcon = L.divIcon({
    html: '<i class="fas fa-home"></i>',
    iconSize: [30, 30],
    className: 'property-icon'
});

const metroIcon = L.divIcon({
    html: '<i class="fas fa-subway"></i>',
    iconSize: [30, 30],
    className: 'metro-icon'
});

const busIcon = L.divIcon({
    html: '<i class="fas fa-bus"></i>',
    iconSize: [30, 30],
    className: 'bus-icon'
});

const attractionIcon = L.divIcon({
    html: '<i class="fas fa-landmark"></i>',
    iconSize: [25, 25],
    className: 'attraction-icon'
});

// Adiciona marcadores
L.marker([propertyLocation.lat, propertyLocation.lng], {
    icon: propertyIcon
}).addTo(map)
.bindPopup("<b>Propriedade</b><br>Preço previsto: $" + flaskData.predictedPrice);

L.marker([metroLocation.lat, metroLocation.lng], {
    icon: metroIcon
}).addTo(map)
.bindPopup("<b>Estação de Metrô</b><br>Distância: " + flaskData.metroDistance + "m");

L.marker([busLocation.lat, busLocation.lng], {
    icon: busIcon
}).addTo(map)
.bindPopup("<b>Ponto de Ônibus</b><br>Distância: " + flaskData.busDistance + "m");

// Adiciona pontos turísticos
attractions.forEach(attraction => {
    L.marker([attraction.lat, attraction.lng], {
        icon: attractionIcon
    }).addTo(map)
    .bindPopup(`<b>${attraction.name}</b><br>Distância: ${attraction.distance}m`);
});

// Adiciona linhas de conexão
const metroLine = L.polyline(
    [[propertyLocation.lat, propertyLocation.lng], [metroLocation.lat, metroLocation.lng]],
    {color: '#FF6319', dashArray: '5, 5'}
).addTo(map);

const busLine = L.polyline(
    [[propertyLocation.lat, propertyLocation.lng], [busLocation.lat, busLocation.lng]],
    {color: '#0039A6', dashArray: '5, 5'}
).addTo(map);