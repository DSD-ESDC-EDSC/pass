$(document).ready(function (){
  var map = initMap();
  addMarker(poi, map);
  addBoundary(demand, map);
});

function initMap(){
  var map = L.map('map').setView([45.5833,-73.6510], 10);

  L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      maxZoom: 18,
      id: 'mapbox/streets-v11',
      accessToken: 'pk.eyJ1IjoianVsY29ueiIsImEiOiJjamhzYzdiMGUwMWcwM3FteW16cmNhYmFxIn0.Epbp18qkWUT8g-Cg7ifkuA'
  }).addTo(map);

  return map;
}

function addMarker(markers, map) {
  for (i = 0; i < markers.length; i++) {
    var lng = parseFloat(markers[i].geometry[1]),
      ltd = parseFloat(markers[i].geometry[0]);
    L.marker([lng, ltd]).addTo(map);
  }
}

function addBoundary(boundary, map) {
  L.geoJson(boundary).addTo(map);
}
