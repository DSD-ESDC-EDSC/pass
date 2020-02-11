function initMap(){
  var map = L.map('map').setView([45.5833,-73.6510], 10);
  var tiles = 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}';

  L.tileLayer(tiles, {
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      maxZoom: 18,
      minZoom: 10,
      zoom: 10,
      maxBounds: [-142.0, 41.0, -52.0, 83.0],
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

  // var icon = L.ExtraMarkers.icon({
  //   icon: 'fa-coffee',
  //   prefix: 'fa'
  // });

  var icon = L.icon({
    iconUrl: 'https://cdn2.iconfinder.com/data/icons/currency-map-markers-2/512/xxx040-512.png',
    iconSize: [40,40]
  })

  for (i = 0; i < markers.length; i++) {
    var lng = parseFloat(markers[i].geometry[0]),
      ltd = parseFloat(markers[i].geometry[1]);
    if (type == "marker") {
      L.marker([lng, ltd], {icon:icon}).addTo(map);
    } else {
      L.circleMarker([lng, ltd]).addTo(map, options);
    }
  }
}

function addBoundary(boundary, map) {
  L.geoJson(boundary).addTo(map);
}

function addChoropleth(feature, map) {
  $(".legend").remove()
  //map.removeLayer(geojsonLayer);

  console.log(feature)
  function getColor(d) {
      return d > 1000 ? '#5e4fa2' :
             d > 500  ? '#3288bd' :
             d > 200  ? '#66c2a5' :
             d > 100  ? '#e6f598' :
             d > 50   ? '#fdae61' :
             d > 20   ? '#f46d43' :
             d > 10   ? '#d53e4f' :
                        '#9e0142';
  }

  //var getColor = chroma.scale(['#9e0142', '#5e4fa2']).domain([0, 1000]);

  function style(feature) {
    return {
        fillColor: getColor(feature.properties.pop),
        weight: 0.5,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
    };
  }

  var choropleth = L.geoJson(feature, {style: style}).addTo(map);

  var legend = L.control({position: 'bottomright'});

  legend.onAdd = function (map) {


      var div = L.DomUtil.create('div', 'info legend'),
          grades = [0, 10, 20, 50, 100, 200, 500, 1000],
          labels = [];

      // loop through our density intervals and generate a label with a colored square for each interval
      for (var i = 0; i < grades.length; i++) {
          div.innerHTML +=
              '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
              grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
      }

      return div;
  };

  legend.addTo(map);

  return choropleth;
}
