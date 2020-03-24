$(document).ready(function (){
  var map = initMap();
  var layerGroup = new L.LayerGroup();
  var choropleth;

  layerGroup.addTo(map);
  addMarker(poi, map, "marker");
  slider();
  //addMarker(demand_point, map, "circle");
  // addBoundary(demand, map);
  //addBoundary(region[0], map);
  $("#model").on("click", function(){
    $("#download").remove();
    $("#strong").remove();
    $("#popup-error-model").remove();
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
  $('#model').html('<div id="loader"><div class="loader"></div><div>Loading Scores...</div></div>');

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
      $('#model').html('Calculate Spatial Accessibility Index');
      //map.removeLayer(layer)
      $("#menu").append("<button id='download' class='btn'>Download Scores as CSV</button>");
      $("#download").on("click", function(){
        downloadData(scores)
      });
      $("#menu").append("<strong id='score'></strong>");
    },
    error: function (err){
      $('#model').html('Calculate Spatial Accessibility Index');
      $("#model").append("<span class='popuptext' id='popup-error-model'>Oops... Cannot calculate index for selected area, likely because it is too unpopulated. Please focus on areas more populated</span>");
      $(".popup .popuptext").css("visibility","visible");
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
