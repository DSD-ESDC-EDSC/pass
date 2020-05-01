$(document).ready(function (){
  var map = initMap();
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
    selections = "<div class='label-param'>"+$("#transportation option:selected").text()+"</div>"
    selections += "<div class='label-param'>"+$("#threshold").val()+" km</div>"
    selections += "<div class='label-param'>"+$("#beta option:selected").text()+"</div>"
    selections += "<div class='label-param'>"+$("#supply option:selected").text()+"</div>"
    selections += "<div class='label-param'>"+$("#demand option:selected").text()+"</div>"
    
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
      choropleth = addChoropleth(scores, map, layerGroup);
      
      var downloadIcon = '<div class="map-icon col-lg-6" id="download"><i class="fas fa-file-download"></i></div>',
      toggleIcon = '<div class="map-icon col-lg-6" id="map-toggle"><i class="fas fa-eye-slash"></i></div>';

      $('#model').html('Calculate Spatial Accessibility Index');
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
      $('#model').html('Calculate Spatial Accessibility Index');
      console.log($(request.responseText)[5].innerHTML)
      $("#model").append("<span class='popuptext' id='popup-error-model'>"+$(request.responseText)[5].innerHTML+"</span>");
      $(".popup .popuptext").css("visibility","visible");
    }
  });
}

function slider(){
  $("#threshold").on("change", function(){
    var threshold = $(this).val();
    $("#threshold-value").html(threshold);
  });
}
