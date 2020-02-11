$(document).ready(function (){
  var map = initMap();
  addMarker(poi, map, "marker");
  //addMarker(demand_point, map, "circle");
  // addBoundary(demand, map);
  //addBoundary(region[0], map);
});

function initMap(){
  var map = L.map('map').setView([45.5833,-73.6510], 10);
  var tiles = 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}';
  //var tiles =  'http://localhost:8000/{z}/{x}/{y}.mvt';
  //var tiles =  'http://10.54.61.201:5050/tiles/{z}/{x}/{y}';

  L.tileLayer(url, {
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      maxZoom: 18,
      zoom: 10,
      maxBounds: [-142.0, 41.0, -52.0, 83.0],
      id: 'mapbox/streets-v11',
      accessToken: 'pk.eyJ1IjoianVsY29ueiIsImEiOiJjamhzYzdiMGUwMWcwM3FteW16cmNhYmFxIn0.Epbp18qkWUT8g-Cg7ifkuA'
  }).addTo(map);

  // var vectorStyle = {
  //   regions: {	// Apply these options to the "water" layer...
  //     fill: true,
  //     weight: 1,
  //     fillColor: '#06cccc',
  //     color: '#06cccc',
  //     fillOpacity: 0.2,
  //     opacity: 0.4
  //   }
  };

  // own vector grid
  var ownTilesLayer = L.vectorGrid.protobuf(tiles, {
    vectorTileLayerStyles: vectorStyle
  });
  console.log(ownTilesLayer)
  ownTilesLayer.addTo(map);

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
    var lng = parseFloat(markers[i].geometry[0]),
      ltd = parseFloat(markers[i].geometry[1]);
    if (type == "marker") {
      L.marker([lng, ltd]).addTo(map);
    } else {
      L.circleMarker([lng, ltd]).addTo(map, options);
    }
  }
}

function addBoundary(boundary, map) {
  //   var tileOptions = {
  //       maxZoom: 20,  // max zoom to preserve detail on
  //       tolerance: 5, // simplification tolerance (higher means simpler)
  //       extent: 4096, // tile extent (both width and height)
  //       buffer: 64,   // tile buffer on each side
  //       debug: 0,      // logging level (0 to disable, 1 or 2
  //       indexMaxZoom: 0,        // max zoom in the initial tile index
  //       indexMaxPoints: 100000, // max number of points per tile in the index
  //   };
  //   console.log(boundary)
  //   var tileIndex = geojsonvt(boundary, tileOptions);
  //   var features = tileIndex.getTile(z, x, y);
  //
  //   var layer = L.vectorGrid.slicer(boundary, {
  //     vectorTileLayerStyles: {
  //         sliced: {
  //             radius: 1,
  //         }
  //     }
  // }).addTo(map);
  //L.geoJson(boundary).addTo(map);
}

function tiles(map){
  // var x = {'x': $('#select-availability').val()},
  //     y = {'y': $('#select-interest').val()},
  //     z = {'z': $('#select-preparedness').val()};
  // var values = $.extend(x, y, z);
  // values = JSON.stringify(values);
}
