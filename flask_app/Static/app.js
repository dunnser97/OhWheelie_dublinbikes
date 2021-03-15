// Function for index page
let map;
function initMap(){
    fetch("/stations").then(response => {
     return response.json(); }).then(data => {
    console.log("data:", data);



  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 53.28853, lng: -6.174522},
    zoom: 13,
  });

    data.forEach(station => {
           const infowindow = new google.maps.InfoWindow({
                    content: station.address + '<br>' + station.available_bikes + ' bikes available'
                      + " " +  '<button onclick="station_details(\'' + station.id + '\'); change_url(\'' + station.id + '\') ">Station Details</button>'
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
            console.log('here')
            var station_output = "<table>";
            station_output += "<tr><th>Station</th><th>Available Bikes</th><th>Available Stands</th><th>Current Time</th></tr>";

            data2.forEach(station => {
                if (station.id == picked){
                console.log(station.address)

                station_output += "<tr><td>" + station.address + "</td>";
                station_output += "<td>" + station.available_bikes+ "</td>"
                station_output += "<td>" + station.available_bike_stands + "</td>";
                station_output += "<td>" + station.time + "</td></tr>";
                }
            })
            station_output += "</table>";
            document.getElementById("over_map").innerHTML = station_output;
        })
}


function change_url(x){
        document.getElementById('weather_map').innerHTML = 'Getting weather data...';
       url = "/index/" + x
    window.history.pushState('page2', 'Title', url);
    fetch("/index/"+ x).then(response => {
     return response.json(); }).then(data => {
     console.log("data:", data);

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
    // console.log(current_time)


            console.log('here')
            var weather_output = "<table>";
            weather_output += "<tr><th>Current Weather</th><th>Time</th>"
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
        window.history.replaceState('page2', 'Title', "/index")
}
 