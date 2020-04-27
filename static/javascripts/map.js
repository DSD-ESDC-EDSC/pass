function initMap(){
  var map = L.map('map').setView([49.2573,-123.1241], 10);
  var tiles = 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}';

  // TO COMPLETE: https://github.com/stefanocudini/leaflet-search/blob/master/examples/geocoding-nominatim.html
  map.addControl( new L.Control.Search({
		url: 'https://nominatim.openstreetmap.org/search?format=json&q={s}',
		jsonpParam: 'json_callback',
		propertyName: 'display_name',
		propertyLoc: ['lat','lon'],
		marker: false,
		collapsed: false,
    autoCollapse: true,
		autoType: false,
		minLength: 2,
    textPlaceholder: "Search area of interest..."
	}) );

  L.tileLayer(tiles, {
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      maxZoom: 18,
      minZoom: 5,
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
    fillOpacity: 1
    // className: 'marker-cluster'
  };

  var getColour = chroma.scale(['#9e0142', '#5e4fa2']).domain([0, 1000]);

  // var icon = L.ExtraMarkers.icon({
  //   icon: 'fa-coffee',
  //   prefix: 'fa'
  // });

  var icon = L.icon({
    iconUrl: 'https://cdn4.iconfinder.com/data/icons/flags-of-the-world-set-1/100/.svg-5-512.png',
    iconSize: [40,40]
  })

  for (i = 0; i < markers.features.length; i++) {
    var lng = markers.features[i].geometry.coordinates[1],
      ltd = markers.features[i].geometry.coordinates[0],
      popupContent = addPopupContent(markers.features[i].properties);
    if (type == "marker" && markers.features.length <= 700) {
      L.marker([lng, ltd], {icon:icon}).bindPopup(popupContent).addTo(map);
    } else if (type == "marker" && markers.features.length > 700) {
      var clusters = new L.MarkerClusterGroup();
      clusters.addLayer(L.marker([lng, ltd], {icon:icon}).bindPopup(popupContent));
    } else {
      L.circleMarker([lng, ltd], options).bindPopup(popupContent).addTo(map);
    }
  }
  if (clusters) {
    clusters.addTo(map)
  }
}

function addBoundary(boundary, map) {
  L.geoJson(boundary).addTo(map);
}

function addPopupContent(properties) {
  var rows = "";
  for (var property in properties) {
    console.log(property)
    var key = property,
      value = properties[property];
      rows += "<tr><td class='tbl-var'>" + key + ":</td><td>" + value + "</td></tr>";
  }
  var content = "<table>" + rows + "</table>";
  return content;
}

function addChoropleth(features, map, layerGroup) {
  // remove existing legend and choropleth
  $("#legend").html('');

  layerGroup.eachLayer(function(layer) {
    map.removeLayer(layer)
  })
  
  var max = features.max,choroplethStats = new geostats(features.score_vals),
      classes = choroplethStats.getQuantile(5),
      names = ['Least Accessible', 'Less Accessible', 'Accessible', 'More Accessible', 'Most Accessible'],
      getColour = chroma.scale(['#d7191c','#ffffbf','#1a9641']).domain([0,max]).classes(classes);
      

  // function for styling choropleth
  function style(features) {
    return {
        fillColor: getColour(features.properties.score),
        weight: 0.5,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
    };
  }

  function onMouseover(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 5,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });
    
    var popupContent = addPopupContent(layer.feature.properties);
    layer.bindPopup(popupContent);
    info.update(layer.feature.properties);
  }

  function onMouseout(e) {
    choropleth.resetStyle(e.target);
    info.update();
  }
  // function for mouse events specific to choropleth
  function onEachFeature(feature, layer) {
      layer.on({
          mouseover: onMouseover,
          mouseout: onMouseout
      });
  }

  // create choropleth map layer and add to layerGroup
  var choropleth = L.geoJson(features, {style: style, onEachFeature: onEachFeature}).addTo(map);
  layerGroup.addLayer(choropleth);
  
  $("#legend").append(buildLegend(classes, getColour, names));

  return choropleth;
}

function buildLegend(classes, getColour, names) {
    
    $('#legend').show();
    $("#map-toggle button").show();
    var legend = '<div class="legend-title"><i class="fa fa-info-circle" title="Classes defined by quintiles"></i></a><strong>Accessibility Index Classes</strong></div>';
    
    // legend for class scale
    for (var i in classes){
      if (names[i]){
        legend += '<div><span style="background-color:'+getColour(classes[i]).hex()+'"></span>'+names[i]+'</div>';
      }
    }
    legend += '<div><span style="background-color:transparent"></span>No Data</div>';
    legend += '<div id="legend-score"></div>';
    
    // legend for gradient scale
    // var s = '';
    // var dom = getColour.domain ? getColour.domain() : [0,max],
    //     dmin = Math.min(dom[0], dom[dom.length-1]),
    //     dmax = Math.max(dom[dom.length-1], dom[0]);
    // 
    // s = '<span class="domain domain-min">'+dmin+'</span>';
    // for (var i=0;i<=100;i++) {
    //   if (i != 50){
    //     s += '<span class="grad-step" style="background-color:'+getColour(dmin + i/100 * (dmax - dmin))+'"></span>';
    //   } else {
    //     s += '<span class="domain domain-med">'+((dmin + dmax)*0.5)+'</span>';
    //   }
    // }
    // 
    // s += '<span class="domain domain-max">'+dmax+'</span>';
    // legend = '<div class="gradient">'+s+'</div>';
    
    return legend;
  }
