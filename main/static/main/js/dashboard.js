
function getDateFromString(strDate){
  // expecting strings like: 
  // Jan. 24, 2018, 3:42 p.m.
  // should match what is rendered when viewing a pledge

  var months = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]

  var year = Number(strDate.split(' ')[2].replace(/,\s*$/, ""))
     month = months.indexOf(strDate.split(' ')[0])
       day = Number(strDate.split(' ')[1].replace(/,\s*$/, ""))
      hour = Number(strDate.split(' ')[3].split(':')[0])
       min = Number(strDate.split(' ')[3].split(':')[1])
  
  // handle some edge cases
  if (isNaN(hour))
    hour = 12 //always assuming "noon" versus "midnight"

  if (isNaN(min))
    min = 0

  // convert am/pm to 24 hour format
  if ( strDate.split(' ')[4] == "p.m.") 
    if ( hour != 12 )
      hour = hour + 12
  
  return new Date(year, month, day, hour, min)
}


function insertHourMarkers(){
  // need an array to push elements to for comparison
  var ar = new Array();

  // find any elements with a createdate in the beginning of its ID
  $("span[id^='createdate_']").each(function (i, el) {
    ar.push(el)
    var currentDate = getDateFromString(el.textContent)
    if ( i > 0 ){
      var previousDate = getDateFromString(ar[i-1].textContent)
      
      if(previousDate.getHours() != currentDate.getHours() ) 
        if(!document.getElementById(Date.parse(currentDate))) // Date.parse here for epoch used in the ids to prevent duplication over days
          $(el).parents().eq(3).before('<div class="HourSeparator" id="' + Date.parse(currentDate) +'">' + currentDate.toLocaleString('en-US', { hour: 'numeric', hour12: true }) + '</div>')
          // this last line is kinda wierd.  We're going to the 3rd parent element to insert a new div with an id of the epoch. 
          // It is this 3rd parent which puts us on the same level as all the other panel div's that the accordion is expanding.
          // We specify id of the epoch for the currentDate so we hopefully don't insert duplicates each time this function is run
          // the HourSeparator class can/should be styled in the dashboard.css 
    }
  });
}


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
  
      $.get('/', function (response) {
        var source = $(''+response+'');
        $('#summary').html(source.find('#summary').html());
      });
      
      data.show('normal');
      insertHourMarkers();
    }
  });
};

setInterval("updateEntries()",3000);



$(document).ready(function() {
  
  $("#spinner").hide();
  
  $.get("/static/main/js/entryeffects.js");
  
 
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
  });
  // End Thanked handler

  insertHourMarkers();

});
