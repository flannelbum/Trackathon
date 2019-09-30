


// returns the greatest panel-collapse id number on the page
function getLid(){
  
  var lid = $("#latestid").text();
  // create an array
  var ar = new Array();
  // for each element with id that starts with 'id'
  $('.panel-collapse').each(
    function(){
      // add it to the array (only its numeric part)
      ar.push(
        // extract the numeric part to be added in the array
        parseInt( $(this).attr('id').replace('id','') )
      );
  });
  // find the max value in the array
  pagelid = Math.max.apply(Math, ar);
  
  if (pagelid > lid){
    $("#latestid").text(pagelid);
    return pagelid;
  } else {
    return lid;
  };
}


// returns the lowest panel-collapse id number on the page
function getLid2(){
  
  // create an array
  var ar = new Array();
  // for each element with id that starts with 'id'
  $('.panel-collapse').each(
    function(){
      // add it to the array (only its numeric part)
      ar.push(
        // extract the numeric part to be added in the array
        parseInt( $(this).attr('id').replace('id','') )
      );
  });
  // find the max value in the array
  pagelid = Math.min.apply(Math, ar);
  return pagelid;
}


function updateSummary(){
    $.get('/', function (response) {
        var source = $(''+response+'');
        $('#summary').html(source.find('#summary').html());
      });
}


// runs every 3 seconds to check for new entries
function updateEntries(){
  //update list of entries
  $.get('/ajax_retrieve_latest_entries/', { 'lid':getLid(), }, function(rawdata, status) {
    if (status == 'success' ) {
      
      var data = $(rawdata).hide();
      $(data).find(".hoverclick").addClass("new");

      $("#accordion").prepend(data);
       
      var $thankbox = $(data).find(".thankbox");
      
      $thankbox.click(function(event){
        var id = $(this).closest('.panel-collapse').prop('id')
        var csrf = $("input[name='csrfmiddlewaretoken'").attr('value');
        $(this).closest(".panel-collapse").parent().find('.glyphicon-alert').remove();
        $(this).attr("disabled", true);
        $.post("/ajax_thank_id/", { 'thankedid': id, 'csrfmiddlewaretoken': csrf })
      });
  
      // request the dashboard but only pull and update the #summary
      updateSummary();
      
      data.show('normal');
      insertHourMarkers(); // from  /static/main/js/insertingDateFunctions.js
    }
  });
};

setInterval("updateEntries()",3000);



$(document).ready(function() {
  
  $("#spinner").hide();
  
//  $.get("/static/main/js/entryeffects.js");
  
 
  // Start Hide/Show
  
  
  $("#hs_totals").click(function(event){
    var text = $(this).text();
    if (text == "Hide Totals") {
      $(this).text("Show Totals");
    } else {
      $(this).text("Hide Totals");
    }
  });
  
  
  
  // End Hide/Show

  // Start auto scroll
  
  $(window).data('ajaxready', true).scroll(function(){
  if ($(window).data('ajaxready') == false) return;

  var scrollTop = $(document).scrollTop();
  var windowHeight = $(window).height();
  var bodyHeight = $(document).height() - windowHeight;
  var scrollPercentage = (scrollTop / bodyHeight);
  var lid = getLid2();
  
  // if the scroll is more than 90% from the top, load more content.
  if (lid > 1) {
    if(scrollPercentage > 0.90) {
      $(window).data('ajaxready', false);
      // console.log("bottom");
    	//ajax get of next data
    	$("#spinner").show();
    	$.get('/ajax_get_next_entries/', { 'lid': lid }, function(rawdata, status) {
        if (status == 'success' ) {
          
          
          var data = $(rawdata);
          
          $(data).find(".thankbox").click(function(event){
            var id = $(this).closest('.panel-collapse').prop('id')
            var csrf = $("input[name='csrfmiddlewaretoken'").attr('value');
            $(this).closest(".panel-collapse").parent().find('.glyphicon-alert').remove();
            $(this).attr("disabled", true);
            $.post("/ajax_thank_id/", { 'thankedid': id, 'csrfmiddlewaretoken': csrf })
            updateSummary();
          });
          
          $("#spinner").hide();
          $("#accordion").append(data);
          $.get("/static/main/js/entryeffects.js");
          $(window).data('ajaxready', true);
          insertHourMarkers();
        }
      	})
      }
    }
  });
  // End auto scroll
  
  
  // Begin sticky scroll
  scrollIntervalID = setInterval(sticky_relocate, 10);
  
  
  function sticky_relocate() {
    var window_top = $(window).scrollTop();
    var div_top = $('#sticky-anchor').offset().top;
    if (window_top > div_top) {
        $('#sticky').addClass('stick');
        $('#sticky-anchor').height($('#sticky').outerHeight());
        
        //$('#sticky').width($('#sticky').width());
//        $('#sticky').width($('#sticky-anchor').width());
        
        
        $(window).scrollTop(window_top);
    } else {
        $('#sticky').removeClass('stick');
        $('#sticky-anchor').height(0);
        
//        $('#sticky').width($('#sticky').width());
        $('#sticky').width($('#sticky-anchor').width());
        
    }
  }
  // End sticky scroll
  
  
  // Start Thanked handler
  $(".thankbox").click(function(event){
    var id = $(this).closest('.panel-collapse').prop('id')
    var csrf = $("input[name='csrfmiddlewaretoken'").attr('value');
    $(this).closest(".panel-collapse").parent().find('.glyphicon-alert').remove();
    $(this).attr("disabled", true);
    $.post("/ajax_thank_id/", { 'thankedid': id, 'csrfmiddlewaretoken': csrf })
    updateSummary()
  });
  // End Thanked handler

  insertHourMarkers();

});
