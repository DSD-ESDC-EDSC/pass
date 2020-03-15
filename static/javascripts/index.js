$(document).ready(function (){
  var map = initMap();
  var layerGroup = new L.LayerGroup();
  var choropleth;

  layerGroup.addTo(map)
  addMarker(poi, map, "marker");
  slider();
  //addMarker(demand_point, map, "circle");
  // addBoundary(demand, map);
  //addBoundary(region[0], map);
  $("#model").on("click", function(){
    $("#download").remove();
    runModel(map, layerGroup);
  })
});

function runModel(map, layerGroup){
  var beta = {'beta': $('#beta').val()},
      transportation = {'transportation': $('#transportation').val()},
      bounds = {'bounds': map.getBounds()},
      threshold = {'threshold': $("#threshold").val()};

  var values = $.extend(beta, transportation, bounds, threshold);
  values = JSON.stringify(values);

  $.ajax({
    type: "POST",
    contentType: "application/json; charset=utf-8",
    url: '/model',
    dataType: 'json',
    data : values,
    async: false,
    cache: false,
    success: function(scores) {
      layer = addChoropleth(scores, map, layerGroup);
      //map.removeLayer(layer)
      $("#menu").append("<button id='download' class='btn'>Download Scores as CSV</button>");
      $("#menu").append("<strong id='score'></strong>");
      $("#download").on("click", function(){
        downloadData(scores)
      });
    },
    error: function (err){
      console.log(err);
    }
  });
}

function slider(){
  $("#threshold").on("change", function(){
    var threshold = $(this).val();
    $("#threshold-value").html(threshold);
  });
}
