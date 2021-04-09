// Functions for index page
let map;

// Initate map
function initMap(){
    fetch("/stations").then(response => {
     return response.json(); }).then(data => {

   document.getElementById("loading_buffer").style.display = "none";
   document.getElementById("loading").style.display = "none";
   map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 53.3493, lng: -6.2611},
    zoom: 14,
  });

// Check if station zoom needed if coming from individual station page
station_zoom()
// add legend to map
add_legend()


for (var key in data){
    stations = data['stations']
    stations = JSON.parse(stations)
    nearest = data['nearest']
    nearest_address = nearest['address']
    }
    console.log(nearest_address)

//add markers and appropriate icons according to bike availability
stations.forEach(station => {
        if (parseInt(station.available_bikes) < 1){
        var myIcon = ('http://maps.google.com/mapfiles/ms/icons/blue-dot.png')
            }
        else if (parseInt(station.available_bikes) < 5){
        var myIcon = ('http://maps.google.com/mapfiles/ms/icons/red-dot.png')
                }
        else if (parseInt(station.available_bikes) < 10){
        var myIcon = ('http://maps.google.com/mapfiles/ms/icons/orange-dot.png')
            }

        else {
        var myIcon = ('http://maps.google.com/mapfiles/ms/icons/green-dot.png')}

        if (station.address == nearest_address) {
        var myIcon = ('http://maps.google.com/mapfiles/ms/micons/cycling.png')
        }

        console.log(station.address)
        const marker = new google.maps.Marker({
                position: {lat: parseFloat(station.latitude), lng: parseFloat(station.longitude)},
                animation: google.maps.Animation.DROP,
                icon: myIcon,
                map: map,
            });
            // add markers with station details and onclick to show charts
            marker.addListener("click", () => {
                const infowindow = new google.maps.InfoWindow({
                    content: '<h4>' + station.address + '</h4><br><h5>' + station.available_bikes + ' Bikes Available' + '</h5><br><h5>' +
                    station.available_bike_stands + ' Bike Stands Available' + '</h5><br><h5>'
                     + 'Last Updated: ' + station.time.substring(6, 15) + '</h5><br>'
                      + " " +  '<button id="details_button" onclick="change_url(\'' + station.Station_number + '\');drawChart(\'' + station.Station_number + '\')">Station Details</button>'
                })
            infowindow.open(map, marker);

           })
        }) // Print error div if map cannot load
   }).catch(err => {
    console.log(err);
    const errorDiv = document.createElement("div");
    const newContent = document.createTextNode("An error has occurred.The map cannot be loaded at this time.");
     errorDiv.appendChild(newContent);
     var mapdiv = document.getElementById("map");
     document.body.insertBefore(errorDiv, mapdiv);
    })
}

// add legend with google map png files
function add_legend(){
      const legend = document.getElementById("legend");
        const icons = {
      green: {
        name: "More than 10 Free bikes",
        icon: ('http://maps.google.com/mapfiles/ms/icons/green-dot.png'),
      },
      orange: {
        name: "Less than 10 Free Bikes",
        icon: ('http://maps.google.com/mapfiles/ms/icons/orange-dot.png'),
      },
      red: {
        name: "Less than 5 Free Bikes",
        icon: ('http://maps.google.com/mapfiles/ms/icons/red-dot.png'),
      },
      blue: {
        name: "No Free bikes",
        icon: ('http://maps.google.com/mapfiles/ms/icons/blue-dot.png'),
      },
      neareststat: {
        name: "Your Nearest Station",
        icon: ('http://maps.google.com/mapfiles/ms/micons/cycling.png'),
        },
    };

        for (const key in icons) {
          const type = icons[key];
          const name = type.name;
          const icon = type.icon;
          const div = document.createElement("div");
          div.innerHTML = '<img src="' + icon + '"> ' + name;
          legend.appendChild(div);
        }
        // push over map and display
        map.controls[google.maps.ControlPosition.RIGHT_TOP].push(legend);
        document.getElementById("legend").style.display = "block";
}

// change url path according to station to get weather
function change_url(x){
        // change url and get response
       url = "/index/" + x
        window.history.pushState('page2', 'Title', url);
        fetch("/index/"+ x).then(response => {
        return response.json(); }).then(data => {

    // get current date time
    var today = new Date();
    var h = today.getHours();
    var m = today.getMinutes();
    if(m > 30){
     h += 1
     m = ":00"
     }
     else {
        m = ":00"}
    if (h<10){
        current_time = "0" + h.toString() + m + ":00"
        }
    else    {
        current_time = h.toString() + m + ":00"
    }
            var weather_output = "<table>";
            weather_output += "<tr><th>Current Weather</th><th>Weather for:</th>"
            + "<th>Rain Index</th><th>Temperature</th><th>Cloud % Coverage</th></tr>";

            // match weather for current time
            data.forEach(hour => {
                if (hour.clock_time == current_time){
                weather_output += "<tr><td>" + hour.weather_symbol + "</td>";
                weather_output += "<td>" + current_time + "</td>";
                weather_output += "<td>" + hour.rain_val + "</td>";
                weather_output += "<td>" + hour.temp_val + "</td>";
                weather_output += "<td>" + hour.cloudi_val + "</td></tr>"
                }
            })
            weather_output += "</table>";

            // push over map
            weather_mp = document.getElementById('weather_map')
            map.controls[google.maps.ControlPosition.BOTTOM_CENTER].clear();
            map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(weather_mp)
            document.getElementById('weather_map').innerHTML = weather_output;
            document.getElementById("weather_map").style.display = "block";


            // else catch the error and restore url
        }).catch(err => {
         console.log(err);
       document.getElementById('weather_map').innerHTML = '<h3>Sorry! The weather data for this station'
       + '<br>cannot be loaded at this time! <br> Try a different station near me!</h3>';
       weather_mp = document.getElementById('weather_map')
       map.controls[google.maps.ControlPosition.BOTTOM_CENTER].clear();
       map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(weather_mp)
       document.getElementById("weather_map").style.display = "block"; })
      restore_url();
}


// draw weather charts using changed url
 function drawChart(x) {
      try {
      // load google charts
        google.charts.load('current', {packages: ['corechart']});
        url = "/index/" + x
        window.history.pushState('page2', 'Title', url);
        fetch("/index/"+ x).then(response => {
        return response.json(); }).then(data => {

        // push the rain and time values to display array
        var array = [];
        var Header= ['Time', 'Rain Index'];
        array.push(Header);
        data.forEach(hour => {
        var temp=[];
            temp.push(hour.clock_time, parseFloat(hour.rain_val));
            array.push(temp);
             })

            // set options for the chart display
           var options = {
          title: 'Rain Index for Station ' + x,
          vAxis: {title: 'mm',  titleTextStyle: {color: '#333'},
          ticks: [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25]}
        };
            try{
          var chart = google.visualization.arrayToDataTable(array)
          document.getElementById('loading_buffer').innerHTML = 'Scroll down for rain forecast!';
          var chart_div = new google.visualization.ColumnChart(document.getElementById("columnchart_values"));
          chart_div.draw(chart, options)

          }
          // catch errors if charts cannot be loaded
          catch {
          document.getElementById('columnchart_values').innerHTML = '<h3>The weather charts cannot be loaded at this time</h3>';
          document.getElementById("columnchart_values").style.display = "block";
          restore_url()
          }

        // catch errror if invalid response returned from json
           }).catch(err => {
        console.log(err);
        document.getElementById('columnchart_values').innerHTML = '<h3>The weather charts for'+
         ' station ' + x + ' cannot be loaded at this time</h3>';
         restore_url()
        document.getElementById("columnchart_values").style.display = "block";

    })
        // display chart
        document.getElementById("columnchart_values").style.display = "block";
        restore_url();
       }

        // catch all errors in external function and restore url
        catch(err) {
        console.log(err)
        document.getElementById('columnchart_values').innerHTML = '<h3>The weather charts for' +
          'station ' + x + ' cannot be loaded at this time</h3>';
        document.getElementById("columnchart_values").style.display = "block";
        restore_url();
        }
        draw_avg_bikes(x)
        link_to_station(x)
     }

// charts for average bikes in given station
function draw_avg_bikes(x) {
        localStorage.setItem('station', x);
        // change url and get response
        fetch("/index/"+ x + "/chart").then(response => {
        return response.json(); }).then(data3 => {

        var array = [];
        var Header= ['Time', 'Avg Bikes'];
        array.push(Header);
        // push values to array
        data3.forEach(hour => {
        var temp=[];
            temp.push(hour.T, parseFloat(hour.avg));
            array.push(temp);
             })

        // restore url
         restore_url();
           var options = {
          title: 'Average Bikes per hour for Station ' + x,
          color: ['#e0440e', '#e6693e', '#ec8f6e', '#f3b49f', '#f6c7b6'],
          vAxis: {title: 'Bikes Available',  titleTextStyle: {color: '#333'},
          ticks: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]}
        };
        // display chart
        var chart = google.visualization.arrayToDataTable(array)
         var chart_div = new google.visualization.ColumnChart(document.getElementById("bike_values"));
          chart_div.draw(chart, options)

        }).catch(err => { //catch errors
        console.log(err);
        document.getElementById('bike_values').innerHTML = '<h3>The bike charts for'+
         ' station ' + x + ' cannot be loaded at this time</h3>';
         restore_url();
        document.getElementById("bike_values").style.display = "block";
        })
            // display chart
            document.getElementById("bike_values").style.display = "block";
}

// function to restore index url to access different url paths in flask
function restore_url(){
    window.history.replaceState('page2', 'Title', "/index")
}


// zooms on station when coming from individual station page
function station_zoom(){
        // read local storage from session (see individual station page
        var longcoords = localStorage.getItem("coord");
        var latcoords = localStorage.getItem("coord2");

        // if opening for first time - is null so return
        if (longcoords == null){
        return }

        // else set map to zoom on the given co-ords
        else    {
        var myOptions = {
        center: { lat: parseFloat(latcoords), lng: parseFloat(longcoords)},
        zoom : 20
        };
        map.setOptions(myOptions);
        }
        // clear the storage
        window.localStorage.clear();
}

function link_to_station(x){
    map.controls[google.maps.ControlPosition.RIGHT_CENTER].clear();
    var btn = document.createElement("BUTTON");
    btn.id = 'button1';
    btn.value = x
    btn.setAttribute('onClick', "go_to_station(this.value)");
    btn.innerHTML = "See Station Analysis";
    document.body.appendChild(btn);
    map.controls[google.maps.ControlPosition.RIGHT_CENTER].push(btn);
}

// Goes to individual station page
function go_to_station(x){
        window.location.href = 'allstations/' + x;
        }

// make charts responsive to window size
window.onresize = resize_charts;
function resize_charts(){
    var stat = localStorage.getItem('station')
    if( stat == null) {
    return }
    else {
    draw_avg_bikes(stat)
    drawChart(stat)}
}
