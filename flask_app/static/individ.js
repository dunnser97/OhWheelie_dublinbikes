function Temperature() {
            //Function retrieves json object from /allstations/station_num/temp route on flask
            //Then Parsed through and the temperature forecast is then returned as a line chart
          localStorage.setItem('weather_function', 'temp');
            fetch("/allstations/"+ x +"/temp").then(response => {
                return response.json(); }).then(data => {
                    //intialise the array
                    var array_temp = [];
                    //Intialise the headers that are wanted and push to intialised array
                    var Header = ['Time', 'Temperature']
                    array_temp.push(Header);
                    data.forEach(hour => {
                    //intialise the array for data
                    var temp_hour=[];
                    //loop over clock time and temperature values  and then push to array_temp
                    temp_hour.push(hour.clock_time, parseFloat(hour.temp_val));
                    array_temp.push(temp_hour);
                })
                var options = {
                title: 'Temperature at Station ' + x,
                vAxis: {title: 'Degrees Celsius - \u00B0C',  titleTextStyle: {color: '#333'},
                 //y-axis ticks for the graph
                ticks: [-5, -2.5, 0, 2.5, 5, 7.5, 10, 12.50, 15, 17.5]
            }
        };
        //Use google charts to represent header and data saved in array_temp
        var chart = google.visualization.arrayToDataTable(array_temp)

        var chart_div = new google.visualization.LineChart(document.getElementById("Weather_chart"));
        chart_div.draw(chart, options)
        }).catch(err => {
        console.log(err);
        document.getElementById('Weather_chart').innerHTML = '<h3>The weather charts for'+
         ' this station cannot be loaded at this time</h3>';
         })
        }



 function percipitation() {
            //Function retrieves json object from /index/station_number on flask
            //Then Parsed through and the temperature forecast is then returned as a line chart
            localStorage.setItem('weather_function', 'rain');
            google.charts.load('current', {packages: ['corechart']});
            fetch("/index/"+ x).then(response => {
                return response.json(); }).then(data => {

                var array = [];
                var Header= ['Time', 'Rain Index'];
                array.push(Header);
                data.forEach(hour => {
                    var temp=[];
                    temp.push(hour.clock_time , parseFloat(hour.rain_val));
                    array.push(temp);
                })

            var options = {
            title: 'Rain Index for Station ' + x,
            vAxis: {title: 'mm',  titleTextStyle: {color: '#333'},
            ticks: [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25]}
            };
        var chart = google.visualization.arrayToDataTable(array)
        var chart_div = new google.visualization.ColumnChart(document.getElementById("Weather_chart"));
        chart_div.draw(chart, options)
        }).catch(err => {
        console.log(err);
        document.getElementById('Weather_chart').innerHTML = '<h3>The weather charts for'+
         ' this station cannot be loaded at this time</h3>';
         })
        }
function draw_avg_bikes() {
    //Loads average number of bikes per hour graph on individual pages
    localStorage.setItem('bike_function', 'time');
    fetch("/index/"+ x + "/chart").then(response => {
        return response.json(); }).then(data3 => {
            var array = [];
            var Header= ['Time', 'Avg Bikes'];
            array.push(Header);
            data3.forEach(hour => {
                var temp=[];
                temp.push(hour.T, parseFloat(hour.avg));
                array.push(temp);
            })
            var options = {
                title: 'Average Bikes per hour for Station ' + x,
                color: ['#e0440e', '#e6693e', '#ec8f6e', '#f3b49f', '#f6c7b6'],
                vAxis: {title: 'Bikes Available',  titleTextStyle: {color: '#333'},
                ticks: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]}
            };
        var chart = google.visualization.arrayToDataTable(array)
        //Calls the bike values id from the html page and appends the graph to that div
        var chart_div = new google.visualization.ColumnChart(document.getElementById("bike_values"));
        chart_div.draw(chart, options)
    }).catch(err => {
        console.log(err);
        document.getElementById('bike_values').innerHTML = '<h3>The bike charts for'+
         ' this station cannot be loaded at this time</h3>';
         })
            document.getElementById("bike_values").style.display = "block";
        }

function avg_bikes_day() {
    //Loads average number of bikes per day graph on individual pages
    localStorage.setItem('bike_function', 'day');
    fetch("/allstations/"+ x + "/avg_bikes_day").then(response => {
        return response.json(); }).then(data4 => {
            var array = [];
            var Header= ['Time', 'Avg Bikes'];
            array.push(Header);
            data4.forEach(day => {
                var temp=[];
                var weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                temp.push(day.day, parseFloat(day.avg_day));
                array.push(temp);
            })
            var options = {
                title: 'Average Bikes per day for Station ' + x,
                color: ['#e0440e', '#e6693e', '#ec8f6e', '#f3b49f', '#f6c7b6'],
                vAxis: {title: 'Bikes Available',  titleTextStyle: {color: '#333'},
                ticks: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]}
            };
        var chart = google.visualization.arrayToDataTable(array)
        var chart_div = new google.visualization.ColumnChart(document.getElementById("bike_values"));
        chart_div.draw(chart, options)
    }).catch(err => {
        console.log(err);
        document.getElementById('bike_values').innerHTML = '<h3>The bike charts for'+
     ' this station cannot be loaded at this time</h3>';
        })
    document.getElementById("bike_values").style.display = "block";
    }
function timechange()   {
    //Assigns Time for select option loops over 24 hour period in format HH:MM:SS
        var today = new Date();
        var time_link = document.getElementById("times");
        for (i=6; i<24; i++)    {
            current_time = i.toString() + ":00:00"
            time_link.innerHTML = time_link.innerHTML + '<option value="' + i + '">' + current_time + '</option>';
        }
}

Temperature()
draw_avg_bikes()
timechange()

window.onresize = resize_charts;

function resize_charts(){
    var weather_chart = localStorage.getItem('weather_function');
    var bike_chart = localStorage.getItem('bike_function');

    if (weather_chart == null){
            return}
    else if (weather_chart == 'temp'){
    Temperature()}
    else if (weather_chart == 'rain'){
    percipitation() }


    if (bike_chart == null){
            return}
    else if (bike_chart == 'time'){
    draw_avg_bikes()
    }
    else if (bike_chart == 'day')
    avg_bikes_day() }
