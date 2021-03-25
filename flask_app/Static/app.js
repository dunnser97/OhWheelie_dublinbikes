// Function for index page
let map;
function initMap(){
    fetch("/stations").then(response => {
     return response.json(); }).then(data => {

   document.getElementById("loading_buffer").style.display = "none";
   document.getElementById("loading").style.display = "none";
   map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 53.3493, lng: -6.2611},
    zoom: 12,
  });

add_legend()

data.forEach(station => {
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

            const marker = new google.maps.Marker({
                position: {lat: parseFloat(station.latitude), lng: parseFloat(station.longitude)},
                icon: myIcon,
                map: map,
            });
            marker.addListener("click", () => {
                const infowindow = new google.maps.InfoWindow({
                    content: station.address + '<br>' + station.available_bikes + ' bikes available' + '<br>' +
                    station.available_bike_stands + ' available bike stands' + '<br>'
                      + " " +  '<button onclick="station_details(\'' + station.id + '\'); change_url(\'' + station.id + '\');drawChart(\'' + station.id + '\')">Station Details</button>'
                })
            infowindow.open(map, marker);

           })
        })
   }).catch(err => {
    console.log(err);
    })
}


function station_details(picked){
        document.getElementById("over_map").innerHTML = "<p>Retrieving Data</p>";
        fetch("/stations").then(response => {
            return response.json(); }).then(data2 => {

            var station_output = "<table>";
            station_output += "<tr><th>Station</th><th>Available Bikes</th><th>Available Stands</th>"
            + "<th>Last Update</th><th>Station Analysis</th></tr>";

            data2.forEach(station => {
                if (station.id == picked){

                time = station.time;
                var clock_time = time.substring(6, 15);

                station_output += "<tr><td>" + station.address + "</td>";
                station_output += "<td>" + station.available_bikes+ "</td>"
                station_output += "<td>" + station.available_bike_stands + "</td>"
                station_output += "<td>" + clock_time + "</td>"
                station_output += "<td><a href='/allstations/" + station.id + "'>Station Details" + "</a></td></tr>";
                }
            })
            station_output += "</table>";
            document.getElementById("over_map").innerHTML = station_output;
            bike_data = document.getElementById('over_map');
            map.controls[google.maps.ControlPosition.LEFT_CENTER].clear();
            map.controls[google.maps.ControlPosition.LEFT_CENTER].push(bike_data)
            document.getElementById("over_map").style.display = "block";
        })
      }

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
    };
        for (const key in icons) {
          const type = icons[key];
          const name = type.name;
          const icon = type.icon;
          const div = document.createElement("div");
          div.innerHTML = '<img src="' + icon + '"> ' + name;
          legend.appendChild(div);
        }
        map.controls[google.maps.ControlPosition.RIGHT_TOP].push(legend);
        document.getElementById("legend").style.display = "block";
}


function change_url(x){
       document.getElementById('weather_map').innerHTML = 'Getting weather data...';
       weather_mp = document.getElementById('weather_map')
       map.controls[google.maps.ControlPosition.LEFT_BOTTOM].clear();
       map.controls[google.maps.ControlPosition.LEFT_BOTTOM].push(weather_mp)
       document.getElementById("weather_map").style.display = "block";

       url = "/index/" + x
    window.history.pushState('page2', 'Title', url);
    fetch("/index/"+ x).then(response => {
     return response.json(); }).then(data => {

    var today = new Date();
    var h = today.getHours();
    var m = today.getMinutes();
    if(m > 30){
     h += 1
     m = ":00"
     }
     else {
        m = ":00"}
    current_time = h.toString() + m + ":00"

            console.log('here')
            var weather_output = "<table>";
            weather_output += "<tr><th>Current Weather</th><th>Weather for:</th>"
            + "<th>Rain Index</th><th>Temperature</th><th>Cloud % Coverage</th></tr>";

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
            document.getElementById('weather_map').innerHTML = weather_output;

        })
        window.history.replaceState('page2', 'Title', "/index");

       document.getElementById('loading_buffer').innerHTML = 'Getting rain forecast...';
       buffer = document.getElementById('loading_buffer')
       map.controls[google.maps.ControlPosition.BOTTOM_CENTER].clear();
       map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(buffer)
       document.getElementById("loading_buffer").style.display = "block";
}


 function drawChart(x) {
        google.charts.load('current', {packages: ['corechart']});
        url = "/index/" + x
        window.history.pushState('page2', 'Title', url);
        fetch("/index/"+ x).then(response => {
        return response.json(); }).then(data => {

        var array = [];
        var Header= ['Time', 'Rain Index'];
        array.push(Header);
        data.forEach(hour => {
        var temp=[];
            temp.push(hour.clock_time, parseFloat(hour.rain_val));
            array.push(temp);
             })

           var options = {
          title: 'Rain Index for Station ' + x,
          vAxis: {title: 'mm',  titleTextStyle: {color: '#333'},
          ticks: [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25]}
        };
          var chart = google.visualization.arrayToDataTable(array)
          document.getElementById('loading_buffer').innerHTML = 'Scroll down for rain forecast!';
          var chart_div = new google.visualization.ColumnChart(document.getElementById("columnchart_values"));
          chart_div.draw(chart, options)
        })
        document.getElementById("columnchart_values").style.display = "block";
        window.history.replaceState('page2', 'Title', "/index")
     }