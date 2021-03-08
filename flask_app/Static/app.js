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
            const marker = new google.maps.Marker({
                position: {lat: parseFloat(station.latitude), lng: parseFloat(station.longitude)},
             map: map,
            });
            marker.addListener("click", () => {
                const infowindow = new google.maps.InfoWindow({
                    content: station.address + '<br>' + station.available_bikes + ' bikes available'
                });
            infowindow.open(map, marker);
           });
        });
   }).catch(err => {
    console.log(err);
    })
}