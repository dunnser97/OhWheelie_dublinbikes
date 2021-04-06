function Temperature() {
            fetch("/allstations/"+ x +"/temp").then(response => {
                return response.json(); }).then(data => {
                    var array_temp = [];
                    var Header = ['Time', 'Temperature']
                    array_temp.push(Header);
                    data.forEach(hour => {
                    var temp_hour=[];
                    temp_hour.push(hour.clock_time, parseFloat(hour.temp_val));
                    array_temp.push(temp_hour);
                })
                var options = {
                title: 'Temperature at Station ' + x,
                vAxis: {title: 'Degrees Celsius - \u00B0C',  titleTextStyle: {color: '#333'},
                ticks: [-5, -2.5, 0, 2.5, 5, 7.5, 10, 12.50, 15, 17.5]
            }
        };
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
        var today = new Date();
        var h = today.getHours();
        var m = today.getMinutes();
        var test = document.getElementById("times");
        if (m<16 || m > 45)  {
            if (m > 45) {
                h+=1;
            }
            m = ":00";
        }
        else if (m > 15 || m < 46)   {
            m = ":30";
        }
        for (i=h; i<24; i++)    {
            if (m===":30")  {
                current_time = i.toString() + m + ":00"
                test.innerHTML = test.innerHTML + '<option value="' + ((i*60)+30) + '">' + current_time + '</option>';
                var temp = i+1;
                var min_temp = ":00";
                current_time = temp.toString() + min_temp + ":00"
                test.innerHTML = test.innerHTML + '<option value="' + ((temp*60)) + '">' + current_time + '</option>';
            }
            else {
                current_time = i.toString() + m + ":00"
                test.innerHTML = test.innerHTML + '<option value="' + ((i*60)) + '">' + current_time + '</option>';
                current_time = i.toString() + ":30:00"
                test.innerHTML = test.innerHTML + '<option value="' + ((i*60)+30) + '">' + current_time + '</option>';
            }
        }
        for (i=0; i<h; i++)    {
            if (m===":30")  {
                current_time = i.toString() + m + ":00"
                test.innerHTML = test.innerHTML + '<option value="' + ((i*60)+30) + '">' + current_time + '</option>';
                var temp = i+1;
                var min_temp = ":00";
                current_time = temp.toString() + min_temp + ":00"
                test.innerHTML = test.innerHTML + '<option value="' + ((temp*60)) + '">' + current_time + '</option>';
            }
            else {
                current_time = i.toString() + m + ":00"
                test.innerHTML = test.innerHTML + '<option value="' + ((i*60)) + '">' + current_time + '</option>';
                current_time = i.toString() + ":30:00"
                test.innerHTML = test.innerHTML + '<option value="' + ((i*60)+30) + '">' + current_time + '</option>';
            }

        }
                console.log(h);
}
Temperature()
draw_avg_bikes()
timechange()