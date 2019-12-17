//hljs.initHighlighting();

$(document).ready(function (){
  /****************** TOOLTIP *******************/
  // TODO: make init
  $("*[data-toggle='tooltip']").on("mouseenter focus", function(e) {
    if (!$(this).attr("aria-describedby")) {
      var tag = "tt"+new Date().getTime();
      $(this).attr("aria-describedby", tag);
      if (!$(this).attr("data-placement")) {
        $(this).attr("data-placement", "right");
      }
      var tr = $(this);
      $("body").append(
        $("<div>", {id: tag, class: "tooltip fade in "+tr.attr("data-placement")}).append(
          $("<div>", {class: "tooltip-inner"}).text(tr.attr("data-title")),
          $("<div>", {class: "tooltip-arrow"})
        )
      );
      if (tr.attr("data-placement") == "right") {
        $("#"+tag)
          .css("top", tr.offset().top+(tr.height()/2)-($("#"+tag).height()/2))
          .css("left", tr.offset().left+tr.outerWidth(false));

      } else if (tr.attr("data-placement") == "top") {
        $("#"+tag)
          .css("top", tr.offset().top-$("#"+tag).height())
          .css("left", tr.offset().left+(tr.width()/2)-($("#"+tag).width()/2));

      } else if (tr.attr("data-placement") == "bottom") {
        $("#"+tag)
          .css("top", tr.offset().top+tr.outerHeight(false))
          .css("left", tr.offset().left+(tr.width()/2)-($("#"+tag).width()/2));

      } else if (tr.attr("data-placement") == "left") {
        $("#"+tag)
          .css("top", tr.offset().top+(tr.height()/2)-($("#"+tag).height()/2))
          .css("left", tr.offset().left-$("#"+tag).width());

      }
    }
  });
  $("*[data-toggle='tooltip']").on("mouseleave blur", function(e) {
    var ttr = $("#"+$(this).attr("aria-describedby"));
    $(this).removeAttr("aria-describedby");
    ttr.removeClass("in");
    setTimeout(function() {
      ttr.remove();
    }, 225);
  });

  // TODO: ADD CREATION OPTION
  // TODO: ADD RENDERING AND MAKE INIT FUNCTION,
  // RENDER x CLOSE BUTTON, ADD TAGS, ETC
  // ADD ACCESSIBILITY UPDATES USING SELECTIZE EVENTS
  // ADD ACCESSIBILITY AND FORM WHEN GENERATED
  $(".cdk-selectize").selectize();

});
