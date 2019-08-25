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
          $(el).parents().eq(3).before('<div class="HourSeparator" id="' + Date.parse(currentDate) +'">' + currentDate.toLocaleString('en-US', { weekday: 'short', day: 'numeric', month: 'numeric', hour: 'numeric', hour12: true }) + '</div>')
          // this last line is kinda wierd.  We're going to the 3rd parent element to insert a new div with an id of the epoch. 
          // It is this 3rd parent which puts us on the same level as all the other panel div's that the accordion is expanding.
          // We specify id of the epoch for the currentDate so we hopefully don't insert duplicates each time this function is run
          // the HourSeparator class can/should be styled in the dashboard.css 
    }
  });
}