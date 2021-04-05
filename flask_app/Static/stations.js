function filterSearch() {
                var input, filter, table, th, a, i, txtValue;
                input = document.getElementById("userInput");
                table = document.getElementById("resultsTable");
                filter = input.value.toUpperCase();
                th = table.getElementsByClassName("stname");
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
                console.log("data: ", data);

                results_output = "<table id='resultsTable'>"
                results_output += "<tr> <th> Station Name </th> <th> Available Bikes </th> <th> Available Stands </th> </tr>"

                data.forEach(station => {
                    results_output += "<tr class='stname'>";
                    results_output += "<th class='stname'><a href='/allstations/" + station.Station_number + "'>" + station.name + "</a></th>";
                    results_output += "<th>" + station.available_bikes + "</th>";
                    results_output += "<th>" + station.available_bike_stands + "</th>";
                    results_output += "</tr>";
                })
                results_output += "</table>";
                document.getElementById("searchresults").innerHTML = results_output;

            }).catch(err => {
                console.log(err)
                document.getElementById("searchresults").innerHTML = "<h1>Error! The stations cannot be loaded at this time</h1>";
})

