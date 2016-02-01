// This JavaScript program uses D3 to generate radial barchart glyphs
// in the cells of a monthly calendar.
//
// Authors:
//  - Arno Klein, 2016  (arno@sagebase.org)  http://binarybottle.com
//
// Copyright 2016, Sage Bionetworks (sagebase.org), Apache v2.0 License

//----------------------------------------------------------------------------
// Generate random data
//----------------------------------------------------------------------------
// Generate number_of_values random numbers with maximum value max_value:
var randomNumbers = function(number_of_values, max_value, empty_value) { 
    var numbers = [];
    for (var i = 0; i < number_of_values; i++) {
        number = parseInt(Math.random() * (max_value - empty_value)) + empty_value;
        if (number < 0) {
          numbers.push(empty_value);
        } else {
          numbers.push(number);
        }
    }
    return numbers;
};
// Generate 35 lists of random numbers for the days of a month:
function getDataForMonth(number_of_values, max_value, empty_value) {
    var randomData = [];
    for (var i = 0; i < 35; i++) {
        randomData.push(randomNumbers(number_of_values, max_value, empty_value));
    }
    return randomData;
};

//----------------------------------------------------------------------------
// Graph glyphs within a calendar
//----------------------------------------------------------------------------
function drawGraphsForMonthlyData() {

    //------------------------------------------------------------------------
    // Radial barcharts
    //------------------------------------------------------------------------
    // Number of bars per bar chart (2 for pre-/post-medication),
    // each extending from the side of a square (4 sides for 4 activities):
    number_of_sides = 4;  // CURRENTLY FIXED
    number_of_bars = 2;   // CURRENTLY FIXED
    max_value = 11;       // maximum value for randomly generated data
    cap_value = 10;       // value corresponding to radius of circle (e.g., control median)
    empty_value = -1;     // negative value corresponding to missing data
    dates = [31,7,14,21,28,
             1,8,15,22,29,
             2,9,16,23,1,
             3,10,17,24,2,
             4,11,18,25,3,
             5,12,19,26,4,
             6,13,20,27,5]
//    dates2 = [31,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
//              16,17,18,19,20,21,22,23,24,25,26,27,28,29,1,2,3,4];

    // Generate random data:
    data = getDataForMonth(number_of_sides * number_of_bars, max_value, empty_value);

    // Create a radial barchart glyph for each date:
    for (var i = 0; i < 5; i++) {
        for (var j = 0; j < 7; j++) {
            var date = dates[j*5 + i];
            radial_bars(data[i*7 + j], number_of_bars, cap_value, empty_value, date);
        }
    }

    // Create a horizon plot for all dates:
    horizon_plot(); //data, cap_value, empty_value);

    barchart_plot();


    //--------------------------------------------------------------------
    // Radial barchart function
    //--------------------------------------------------------------------
    function radial_bars(data, number_of_bars, cap_value, empty_value, date) { 

        // Plot dimensions:
        bar_width = 15;        // width of each bar in the bar plot (pixels)
        bar_length = 50;       // maximum bar length (in pixels)
        circle_penumbra = 20;  // border between circle and enclosing box (pixels)
        barplot_width = number_of_bars * bar_width;
        total_width = barplot_width + 2 * bar_length;

        // Map data values to plot dimensions: 
        value2length = d3.scale.linear()
           .domain([0, cap_value])
           .range([0, bar_length]);
        plot_y = d3.scale.linear()
           .domain([0, number_of_bars])
           .range([0, barplot_width]);
        translate_y = function(d, index){ return total_width/2 + plot_y(index) - bar_width; };
        translate_x = function(d, i) { return "translate(" + (bar_length + i * bar_width) + ", 0)"; };

        // Break up data into pairs for each of four directions
        // (pre-/post-medication for mPower's voice, stand, tap, and walk activities):
        left_data = [data[0], data[1]];
        right_data = [data[2], data[3]];
        up_data = [data[4], data[5]];
        down_data = [data[6], data[7]];

        // Background colors:
        background_color = "#e2e2e2";  // color of circle behind radial bar chart
        empty_color = "#ffffff";       // color of background calendar squares and empty data
        // Pairs of colors for 4 directions (pre-/post-medication for mPower's 4 activities):
        walk_pre_color = "#20AED8";
        walk_post_color = "#2C1EA2";
        stand_pre_color = "#6E6E6E";
        stand_post_color = "#151515";
        voice_pre_color = "#EEBE32";
        voice_post_color = "#9F5B0D";
        tap_pre_color = "#F78181";
        tap_post_color = "#C02504";
        colors = [walk_pre_color, walk_post_color,
                  stand_pre_color, stand_post_color,
                  voice_pre_color, voice_post_color,
                  tap_pre_color, tap_post_color];
        left_colors = [colors[0], colors[1]];
        right_colors = [colors[2], colors[3]];
        up_colors = [colors[4], colors[5]];
        down_colors = [colors[6], colors[7]];

        // Glyph:
        chart = d3.select('#chart')
        glyph = chart.append('svg')
            .attr('height', total_width)
            .attr('width', total_width)

        // Enclosing circle:
        glyph.selectAll("rect.circle")
            .data(left_data)
          .enter().append("circle")
            .attr("cx", total_width/2)
            .attr("cy", total_width/2)
            .attr("r", total_width/2)
            .style("stroke", "#ffffff")
            .style("stroke-width", circle_penumbra)
            .style("fill", background_color)

        // LEFT missing data:
        glyph.selectAll("rect.leftempty")
            .data(left_data)
          .enter().append("rect")
            .attr("x", 0)
            .attr("y", translate_y)
            .attr("width", bar_length)
            .attr("height", bar_width)
            .style("fill", function(d, i) { 
              if (left_data[i] == empty_value) { return empty_color; }
              else { return "transparent"; } })
            .attr("class", "gray");

        // LEFT data:
        glyph.selectAll("rect.left")
            .data(left_data)
          .enter().append("rect")
            .attr("x", function(pos) { return bar_length - value2length(pos); })
            .attr("y", translate_y)
            .attr("width", value2length)
              //function(d, i) { 
              //if (left_data[i] != empty_value) { return value2length; }})
            .attr("height", bar_width - 1)
            .style("fill", function(d, i) { return left_colors[i]; })
            .attr("class", "left");

        // RIGHT missing data:
        glyph.selectAll("rect.rightempty")
            .data(right_data)
          .enter().append("rect")
            .attr("x", bar_length + barplot_width)
            .attr("y", translate_y)
            .attr("width", bar_length)
            .attr("height", bar_width)
            .style("fill", function(d, i) { 
              if (right_data[i] == empty_value) { return empty_color; }
              else { return "transparent"; } })
            .attr("class", "gray");

        // RIGHT data:
        glyph.selectAll("rect.right")
            .data(right_data)
          .enter().append("rect")
            .attr("x", bar_length + barplot_width)
            .attr("y", translate_y)
            .attr("width", value2length)
              //function(d, i) { 
              //if (right_data[i] != empty_value) { return value2length; }})
            .attr("height", bar_width - 1) 
            .style("fill", function(d, i) { return right_colors[i]; })
            .attr("class", "right");

        // UP missing data:
        glyph.selectAll("rect.upempty")
            .data(up_data)
          .enter().append("rect")
            .attr("transform", translate_x)
            .attr("y", 0)
            .attr("height", bar_length)
            .attr("width", bar_width)
            .style("fill", function(d, i) { 
              if (up_data[i] == empty_value) { return empty_color; }
              else { return "transparent"; } })
            .attr("class", "gray");

        // UP data:
        glyph.selectAll("rect.up")
            .data(up_data)
          .enter().append("rect")
            .attr("transform", translate_x)
            .attr("y", function(pos) { return total_width/2 - value2length(pos) - bar_width; })
            .attr("height", value2length)
              //function(d, i) { 
              //if (up_data[i] != empty_value) { return value2length; }})
            .attr("width", bar_width - 1)
            .style("fill", function(d, i) { return up_colors[i]; })
            .attr("class", "up");

        // DOWN missing data:
        glyph.selectAll("rect.downempty")
            .data(down_data)
          .enter().append("rect")
            .attr("transform", translate_x)
            .attr("y", total_width/2 + bar_width)
            .attr("height", bar_length)
            .attr("width", bar_width)
            .style("fill", function(d, i) { 
              if (down_data[i] == empty_value) { return empty_color; }
              else { return "transparent"; } })
            .attr("class", "gray");

        // DOWN data:
        glyph.selectAll("rect.down")
            .data(down_data)
          .enter().append("rect")
            .attr("transform", translate_x)
            .attr("y", total_width/2 + bar_width)
            .attr("height", value2length)
              //function(d, i) { 
              //if (down_data[i] != empty_value) { return value2length; }})
            .attr("width", bar_width - 1)
            .style("fill", function(d, i) { return down_colors[i]; })
            .attr("class", "down");

        // Center square:
        rect = glyph.append('rect')
            .attr('width', barplot_width)
            .attr('height', barplot_width)
            .attr('x', total_width/2 - bar_width)
            .attr('y', total_width/2 - bar_width)
            //.style("stroke", "#aaaaaa")
            //.style("stroke-width", 1)
            .style("fill", background_color);

        // Enclosing square:
        rect = glyph.append('rect')
            .attr('width', total_width)
            .attr('height', total_width)
            .attr('x', 0)
            .attr('y', 0)
            .style("stroke", "#aaaaaa")
            .style("stroke-width", 1)
            .style("fill", "transparent");

        // Date text:
        text = glyph.append('text')
            .attr('x', 4)
            .attr('y', 16)
            .style('fill', 'black')
            .style('font-size', '9pt')
            .text(date)
    }


    //------------------------------------------------------------------------
    // Horizon (area) plot function
    //------------------------------------------------------------------------
    // (http://tympanus.net/codrops/2012/08/29/multiple-area-charts-with-d3-js/)
    function horizon_plot() {  //data, cap_value, empty_value) {

        var max_value = 1;

        var margin = {top: 10, right: 40, bottom: 150, left: 60},
            width = 980 - margin.left - margin.right,
            height = 500 - margin.top - margin.bottom,
            contextHeight = 50,
            contextWidth = width * .5;

        var svg = d3.select("#chart2").append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", (height + margin.top + margin.bottom));

//        var parseDate = d3.time.format("%y-%b-%d").parse,
//            formatPercent = d3.format(".0%");

        d3.csv('./data.csv', createChart);

        function createChart(data){
          var activities_pre = [];
          var activities_post = [];
          var charts1 = [];
          var charts2 = [];
          var maxDataPoint = 0;

          //data.forEach(function(d) {
          //  d.Date = parseDate(d.Date);
          //});

          /* Loop through first row and get each activity
            and push odd columns into premed and even columns
            into postmed activity arrays to use later */
          var col = 0;
          for (var prop in data[0]) {
            if (data[0].hasOwnProperty(prop)) {
              if (prop != 'Date') {
                col = col + 1;
                if (col % 2 == 0) {
                  activities_post.push(prop)
                } else {
                  activities_pre.push(prop)
                }
              }
            }
          };

          var activitiesCount = activities_post.length;
          var startDate = data[0].Date;
          var endDate = data[data.length - 1].Date;
          var chartHeight = height * (1 / activitiesCount);
          
          // Let's make sure these are all numbers, 
          // we don't want javaScript thinking it's text 
          // Let's also figure out the maximum data point
          // We'll use this later to set the Y-Axis scale
          data.forEach(function(d) {
            for (var prop in d) {
              if (d.hasOwnProperty(prop)) {
                d[prop] = parseFloat(d[prop]);
                if (d[prop] > maxDataPoint) {
                  maxDataPoint = d[prop];
                }
              }
            }
            
            // D3 needs a date object, let's convert it just one time
            //d.Date = new Date(d.Date,0,1);
          });
    
          for(var i = 0; i < activitiesCount; i++){
            charts1.push(new Chart({
                                  data: data.slice(),
                                  id: i,
                                  name: activities_post[i],
                                  width: width,
                                  height: height * (1 / activitiesCount),
                                  maxDataPoint: maxDataPoint,
                                  svg: svg,
                                  margin: margin,
                                  showBottomAxis: (i == activities_post.length - 1)
                                }));
          }
          for(var i = 0; i < activitiesCount; i++){
            charts2.push(new Chart({
                                  data: data.slice(),
                                  id: i,
                                  name: activities_pre[i],
                                  width: width,
                                  height: height * (1 / activitiesCount),
                                  maxDataPoint: maxDataPoint,
                                  svg: svg,
                                  margin: margin,
                                  showBottomAxis: (i == activities_post.length - 1)
                                }));
          }

          // Let's create the context brush that will let us zoom and pan the chart
          var contextXScale = d3.time.scale()
                                .range([0, contextWidth])
                                .domain(charts1[0].xScale.domain()); 
          var contextAxis = d3.svg.axis()
                                  .scale(contextXScale)
                                  .tickSize(contextHeight)
                                  .tickPadding(-10)
                                  .orient("bottom");
          var contextArea = d3.svg.area()
                                  .interpolate("linear")  //*cardinal")
                                  .x(function(d) { return contextXScale(d.Date); })
                                  .y0(contextHeight)
                                  .y1(0);
          var brush = d3.svg.brush()
                            .x(contextXScale)
                            .on("brush", onBrush);
          var context = svg.append("g")
                            .attr("class","context")
                            .attr("transform", "translate(" + (margin.left + width * .25) + "," + (height + margin.top + chartHeight) + ")");

          context.append("g")
                            .attr("class", "x axis top")
                            .attr("transform", "translate(0,0)")
                            .call(contextAxis)
          context.append("g")
                            .attr("class", "x brush")
                            .call(brush)
                            .selectAll("rect")
                              .attr("y", 0)
                              .attr("height", contextHeight);

          context.append("text")
                    .attr("class","instructions")
                    .attr("transform", "translate(140," + (contextHeight - 24) + ")")
                    .text('Click and drag to zoom');

          function onBrush(){
            /* this will return a date range to pass into the chart object */
            var b = brush.empty() ? contextXScale.domain() : brush.extent();
            for(var i = 0; i < activitiesCount; i++){
              charts1[i].showOnly(b);
              charts2[i].showOnly(b);
            }
          }
        }

        function Chart(options){
          this.chartData = options.data;
          this.width = options.width;
          this.height = options.height;
          this.maxDataPoint = options.maxDataPoint;
          this.svg = options.svg;
          this.id = options.id;
          this.name = options.name;
          this.margin = options.margin;
          this.showBottomAxis = options.showBottomAxis;

          var localName = this.name;

          /* XScale is time based */
          this.xScale = d3.time.scale()
                                .range([0, this.width])
                                .domain(d3.extent(this.chartData.map(function(d, i) { return d.Date; })));

          /* YScale is linear based on the maxData Point we found earlier */
          this.yScale = d3.scale.linear()
                                .range([this.height,0])
                                .domain([0, max_value]); //this.maxDataPoint]);
          var xS = this.xScale;
          var yS = this.yScale;
          
          /* This is what creates the chart.
             There are a number of interpolation options. 
            'basis' smooths it the most, however, when working with a lot of data, this will slow it down 
          */
          this.area = d3.svg.area()
                                .interpolate("linear")  //"cardinal")  //"linear")
                                .x(function(d) { return xS(d.Date); })
                                .y0(this.height)
                                .y1(function(d) { return yS(d[localName]); });
          /* This isn't required - it simply creates a mask. If this weren't here,
             when we zoom/panned, we'd see the chart go off to the left under the y-axis */
          this.svg.append("defs").append("clipPath")
                                  .attr("id", "clip-" + this.id)
                                  .append("rect")
                                    .attr("width", this.width)
                                    .attr("height", this.height);
          /* Assign it a class so we can assign a fill color and position it on the page */
          this.chartContainer = svg.append("g")
                                    .attr('class',this.name.toLowerCase())
                                    .attr("transform", "translate(" + this.margin.left + "," + (this.margin.top + (this.height * this.id) + (10 * this.id)) + ")");
    
          /* We've created everything, let's actually add it to the page */
          this.chartContainer.append("path")
                              .data([this.chartData])
                              .attr("class", "chart")
                              .attr("clip-path", "url(#clip-" + this.id + ")")
                              .attr("d", this.area);
                          
          /* We only want a top axis if it's the first activity */
          /*
          this.xAxisTop = d3.svg.axis().scale(this.xScale).orient("top");
          if(this.id == 0){
            this.chartContainer.append("g")
                  .attr("class", "x axis top")
                  .attr("transform", "translate(0,0)")
                  .call(this.xAxisTop);
          }
          */
          /* Only want a bottom axis on the last activity */
          this.xAxisBottom = d3.svg.axis().scale(this.xScale).orient("bottom");
          if(this.showBottomAxis){
              this.chartContainer.append("g")
                  .attr("class", "x axis bottom")
                  .attr("transform", "translate(0," + (this.height + 11) + ")")
                  //.tickValues([1, 5, 10, 15, 20, 25, 30])
                  .call(this.xAxisBottom);
            }  
            
          this.yAxis = d3.svg.axis().scale(this.yScale).orient("left").ticks(1);

          this.chartContainer.append("g")
                              .attr("class", "y axis")
                              .attr("transform", "translate(-10,0)")
                              .call(this.yAxis);
          this.chartContainer.append("text")
                              .attr("class","activity-title")
                              .attr("transform", "translate(0,15)")
                              .text(this.name);
        }
        Chart.prototype.showOnly = function(b){
            this.xScale.domain(b);
            this.chartContainer.select("path").data([this.chartData]).attr("d", this.area);
            //this.chartContainer.select(".x.axis.top").call(this.xAxisTop);
            this.chartContainer.select(".x.axis.bottom").call(this.xAxisBottom);
        }
    }


/*
    //------------------------------------------------------------------------
    // Bar chart function
    //------------------------------------------------------------------------
    function barchart_plot() {  //data, cap_value, empty_value) {

      var margin = {top: 20, right: 20, bottom: 30, left: 40},
          width = 960 - margin.left - margin.right,
          height = 500 - margin.top - margin.bottom;
      
      var x = d3.scale.ordinal()
          .rangeRoundBands([0, width], .1);
      
      var y = d3.scale.linear()
          .rangeRound([height, 0]);
      
      var color = d3.scale.ordinal()
          .range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);
      
      var xAxis = d3.svg.axis()
          .scale(x)
          .orient("bottom");
      
      var yAxis = d3.svg.axis()
          .scale(y)
          .orient("left")
          .tickFormat(d3.format(".2s"));
      
      var svg = d3.select("body").append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
        .append("g")
          .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
      
      d3.csv("data.csv", function(error, data) {
        if (error) throw error;
      
        color.domain(d3.keys(data[0]).filter(function(key) { return key !== "State"; }));
      
        data.forEach(function(d) {
          var y0 = 0;
          d.ages = color.domain().map(function(name) { return {name: name, y0: y0, y1: y0 += +d[name]}; });
          d.total = d.ages[d.ages.length - 1].y1;
        });
      
        data.sort(function(a, b) { return b.total - a.total; });
      
        x.domain(data.map(function(d) { return d.State; }));
        y.domain([0, d3.max(data, function(d) { return d.total; })]);
      
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);
      
        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
          .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Population");
      
        var state = svg.selectAll(".state")
            .data(data)
          .enter().append("g")
            .attr("class", "g")
            .attr("transform", function(d) { return "translate(" + x(d.State) + ",0)"; });
      
        state.selectAll("rect")
            .data(function(d) { return d.ages; })
          .enter().append("rect")
            .attr("width", x.rangeBand())
            .attr("y", function(d) { return y(d.y1); })
            .attr("height", function(d) { return y(d.y0) - y(d.y1); })
            .style("fill", function(d) { return color(d.name); });
      
        var legend = svg.selectAll(".legend")
            .data(color.domain().slice().reverse())
          .enter().append("g")
            .attr("class", "legend")
            .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });
      
        legend.append("rect")
            .attr("x", width - 18)
            .attr("width", 18)
            .attr("height", 18)
            .style("fill", color);
      
        legend.append("text")
            .attr("x", width - 24)
            .attr("y", 9)
            .attr("dy", ".35em")
            .style("text-anchor", "end")
            .text(function(d) { return d; });
    });
*/

}


drawGraphsForMonthlyData();


//----------------------------------------------------------------------------
// CALENDAR  (http://www.javascriptkit.com/script/script2/anymonthcal.shtml)
//----------------------------------------------------------------------------
// Any-Month calendar script: Rob Patrick (rpatrick@mit.edu)

//var daysOfTheWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

function setToday() {
var now   = new Date();
var day   = now.getDate();
var month = now.getMonth();
var year  = now.getYear();
if (year < 2000)    // Y2K Fix, Isaac Powell
year = year + 1900; // http://onyx.idbsu.edu/~ipowell
this.focusDay = day;
document.calControl.month.selectedIndex = month;
document.calControl.year.value = year;
//displayCalendar(month, year);
}
function isFourDigitYear(year) {
if (year.length != 4) {
alert ("Sorry, the year must be four-digits in length.");
document.calControl.year.select();
document.calControl.year.focus();
} else { return true; }
}
function selectDate() {
var year  = document.calControl.year.value;
if (isFourDigitYear(year)) {
var day   = 0;
var month = document.calControl.month.selectedIndex;
//displayCalendar(month, year);
    }
}

function setPreviousYear() {
var year  = document.calControl.year.value;
if (isFourDigitYear(year)) {
var day   = 0;
var month = document.calControl.month.selectedIndex;
year--;
document.calControl.year.value = year;
//displayCalendar(month, year);
   }
}
function setPreviousMonth() {
var year  = document.calControl.year.value;
if (isFourDigitYear(year)) {
var day   = 0;
var month = document.calControl.month.selectedIndex;
if (month == 0) {
month = 11;
if (year > 1000) {
year--;
document.calControl.year.value = year;
}
} else { month--; }
document.calControl.month.selectedIndex = month;
//displayCalendar(month, year);
   }
}
function setNextMonth() {
var year  = document.calControl.year.value;
if (isFourDigitYear(year)) {
var day   = 0;
var month = document.calControl.month.selectedIndex;
if (month == 11) {
month = 0;
year++;
document.calControl.year.value = year;
} else { month++; }
document.calControl.month.selectedIndex = month;
//displayCalendar(month, year);
   }
}
function setNextYear() {
var year = document.calControl.year.value;
if (isFourDigitYear(year)) {
var day = 0;
var month = document.calControl.month.selectedIndex;
year++;
document.calControl.year.value = year;
//displayCalendar(month, year);
   }
}
function displayCalendar(month, year) {       
month = parseInt(month);
year = parseInt(year);
var i = 0;
var days = getDaysInMonth(month+1,year);
var firstOfMonth = new Date (year, month, 1);
var startingPos = firstOfMonth.getDay();
days += startingPos;
/*
document.calButtons.calPage.value  =   " Su Mo Tu We Th Fr Sa";
document.calButtons.calPage.value += "\n --------------------";
for (i = 0; i < startingPos; i++) {
if ( i%7 == 0 ) document.calButtons.calPage.value += "\n ";
document.calButtons.calPage.value += "   ";
}
for (i = startingPos; i < days; i++) {
if ( i%7 == 0 ) document.calButtons.calPage.value += "\n ";
if (i-startingPos+1 < 10)
document.calButtons.calPage.value += "0";
document.calButtons.calPage.value += i-startingPos+1;
document.calButtons.calPage.value += " ";
}
for (i=days; i<42; i++)  {
if ( i%7 == 0 ) document.calButtons.calPage.value += "\n ";
document.calButtons.calPage.value += "   ";
}
*/
document.calControl.Go.focus();
}

function getDaysInMonth(month,year)  {
var days;
if (month==1 || month==3 || month==5 || month==7 || month==8 || month==10 || month==12)  days=31;
else if (month==4 || month==6 || month==9 || month==11) days=30;
else if (month==2)  {
if (isLeapYear(year)) { days=29; }
else { days=28; }
}
return (days);
}
function isLeapYear (Year) {
if (((Year % 4)==0) && ((Year % 100)!=0) || ((Year % 400)==0)) {
return (true);
} else { return (false); }
}
