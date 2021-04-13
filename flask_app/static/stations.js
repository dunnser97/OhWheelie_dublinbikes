/* Filter search function which will update the contents of the results table, as the user types. Implementation aided by WW3 schools' Javascript tutorials.*/
function filterSearch() {
    var input, filter, table, th, a, i, txtValue;
    input = document.getElementById("userInput");
    table = document.getElementById("resultsTable");
    
    //Search won't be case sensitive.
    filter = input.value.toUpperCase();
    th = table.getElementsByClassName("stname");
    
    //Anything not matching user query is hidden.
    for (i = 0; i < th.length; i++) {
        a = th[i].getElementsByTagName("a")[0];
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            th[i].style.display = "";
        } else {
            th[i].style.display = "none";
        }
    }

}
fetch("/stations").then(response => {
    return response.json();
}).then(data => {

    for (var key in data){
        stations = JSON.parse(data['stations'])
    }
    console.log(stations)
    //Table begins.
    results_output = "<table id='resultsTable'>"
    results_output += "<tr> <th> Station Name </th> <th> Available Bikes </th> <th> Available Stands </th> </tr>"
    
    //Loop through all stations and add a table row for each station.
    stations.forEach(station => {
        results_output += "<tr class='stname'>";
        results_output += "<th class='stname'><a href='/allstations/" + station.Station_number + "'>" + station.name + "</a></th>";
        results_output += "<th>" + station.available_bikes + "</th>";
        results_output += "<th>" + station.available_bike_stands + "</th>";
        results_output += "</tr>";
    })
    //Table ends.
    results_output += "</table>";
    document.getElementById("searchresults").innerHTML = results_output;

}).catch(err => {
    console.log(err)
    document.getElementById("searchresults").innerHTML = "<h1>Error! The stations cannot be loaded at this time</h1>";
})

