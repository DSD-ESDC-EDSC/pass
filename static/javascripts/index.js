$(document).ready(function (){
  var map = initMap();
  addMarker(poi, map, "marker");
  //addMarker(demand_point, map, "circle");
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

function addMarker(markers, map, type) {
  var options = {
    radius: 3,
    fillColor: "#000",// "#28ea3f",//"#0163FF",
    color: "#000", //"#0163FF",
    weight: 2,
    opacity: 1,
    fillOpacity: 1,
    // className: 'marker-cluster'
  };
  for (i = 0; i < markers.length; i++) {
    var lng = parseFloat(markers[i].geometry[1]),
      ltd = parseFloat(markers[i].geometry[0]);
    if (type == "marker") {
      L.marker([lng, ltd]).addTo(map);
    } else {
      L.circleMarker([lng, ltd]).addTo(map, options);
    }
  }
}

function addBoundary(boundary, map) {
  L.geoJson(boundary).addTo(map);
}
