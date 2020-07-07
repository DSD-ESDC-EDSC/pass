$(document).ready(function (){
  var map = initMap(mapToken);
  var layerGroup = new L.LayerGroup();
  var choropleth;

  layerGroup.addTo(map);
  addMarker(poi[0], map, "marker");
  slider();
  //addMarker(demand_point, map, "circle");
  // addBoundary(demand, map);
  //addBoundary(region[0], map);
  $("#model").on("click", function(){
    $("#map-tools").hide();
    $("#strong").remove();
    $(".gradient").remove();
    $("#popup-error-model").remove();
    runModel(map, layerGroup);
  })
  
  $('#menu-toggle').on('click', function () {
    toggleMenu(false);
  });
  
});

function toggleMenu(toolbar){
  
  if (!toolbar) {
    selections = "<div class='label-param'>Transit: "+$("#transportation option:selected").text()+"</div>"
    selections += "<div class='label-param'>Distance Threshold: "+$("#threshold").val()+" km</div>"
    selections += "<div class='label-param'>Willingness to Drive: "+$("#beta option:selected").text()+"</div>"
    selections += "<div class='label-param'>POI Supply: "+$("#supply option:selected").text()+"</div>"
    selections += "<div class='label-param'>POI Capacity: "+$("#capacity option:selected").text()+"</div>"
    selections += "<div class='label-param'>Population: "+$("#demand option:selected").text()+"</div>"
    
    $("#menu").hide();
    $("#toolbar").html(selections).show();
    $("#menu-toggle-navbar").show();
  } else {
    $("#menu").show();
    $("#toolbar").hide();
    $("#menu-toggle-navbar").hide();
  }
  
  $("#menu-toggle-navbar").on("click", function(){
    toggleMenu(true);
  });
  
  console.log('test')
}

function runModel(map, layerGroup){
  var beta = {'beta': $('#beta').val()},
      transportation = {'transportation': $('#transportation').val()},
      bounds = {'bounds': map.getBounds()},
      threshold = {'threshold': $("#threshold").val()},
      supply = {'supply': $("#supply").val()},
      capacity = {'capacity': $("#capacity").val()}, 
      demand = {'demand': $("#demand").val()};

  var values = $.extend(beta, transportation, bounds, threshold, supply, demand, capacity);
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
      choropleth = addChoropleth(scores, map, layerGroup);
      
      var downloadIcon = '<div class="map-icon col-lg-6" id="download"><i class="fas fa-file-download"></i></div>',
      toggleIcon = '<div class="map-icon col-lg-6" id="map-toggle"><i class="fas fa-eye-slash"></i></div>';

      $('#model').html('Measure Spatial Accessibility');
      $("#legend").append(downloadIcon + toggleIcon);
      $("#map-tools").show();
      $("#download").on("click", function(){
        downloadData(scores)
      });
      $("#map-toggle").on("click", function(e) {
          e.preventDefault();
          if(map.hasLayer(choropleth)) {
              $(this).html('<i class="fas fa-eye"></i>');
              map.removeLayer(choropleth);
          } else {
              map.addLayer(choropleth);  
              $(this).html('<i class="fas fa-eye-slash"></i>');
         }
      });
      $("#menu").append("<strong id='score'></strong>");
    },
    error: function (request, status, message){
      $('#model').html('Measure Spatial Accessibility');
      console.log($(request.responseText)[5].innerHTML)
      $("#model").append("<span class='popuptext' id='popup-error-model'>"+$(request.responseText)[5].innerHTML+"</span>");
      $(".popup .popuptext").css("visibility","visible");
    }
  });
}

function slider(){
  $("#threshold-value").html($("#threshold").val());
  $("#threshold").on("change", function(){
    var threshold = $(this).val();
    $("#threshold-value").html(threshold);
  });
}
