// This JavaScript D3 program generates an mPower performance report
// from mPower Parkinson mobile health data (parkinsonmpower.org.
// Github repository: http://sage-bionetworks.github.io/mhealthx/
//
// Authors:
//  - Arno Klein, 2016  (arno@sagebase.org)  http://binarybottle.com
//
// Copyright 2016, Sage Bionetworks (sagebase.org), Apache v2.0 License
//------------------------------------------------------------------------

//----------------------------------------------------------------------------
// Graph monthly report data
//----------------------------------------------------------------------------
var parseDate = d3.time.format("%Y-%b-%d").parse;
var show_zoom = 0;

// Data:
data_file = './data.txt';
parseDate = d3.time.format("%Y-%b-%d").parse;
parse_year = d3.time.format("%Y");
parse_month = d3.time.format("%B");
parse_date = d3.time.format("%d");

//------------------------------------------------------------------------
// Load data
//------------------------------------------------------------------------
d3.csv(data_file, function(error, data) {

    // Data file:
    max_value = 1;       // maximum value for randomly generated data
    empty_value = -1;     // negative value corresponding to missing data
    control_voice = 0.85; // line to compare with control data
    control_walk = 0.5;   // line to compare with control data
    control_stand = 0.75; // line to compare with control data
    control_tap = 0.68;   // line to compare with control data
    control_values = [control_voice, control_walk, control_stand, control_tap]

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

    // Add month and year to the top of the graphic:
    data.forEach(function(d) {
        d.year = parse_year(parseDate(d.date));
        d.month = parse_month(parseDate(d.date));
    });
    var middate = Math.round(data.length/2);
    document.getElementById("month").innerHTML = data[middate].month;
    document.getElementById("year").innerHTML = data[middate].year;
    // axis label:
    document.getElementById("xaxis_label").innerHTML = "day in " + data[middate].month;

    // Create a horizon plot for all activities and dates:
    horizon_plot(); //data, cap_value, empty_value);

    //------------------------------------------------------------------------
    // Horizon (area) plot function
    //------------------------------------------------------------------------
    // (http://tympanus.net/codrops/2012/08/29/multiple-area-charts-with-d3-js/)
    function horizon_plot() {

        var margin = {top: 10, right: 40, bottom: 150, left: 60},
            width = 980 - margin.left - margin.right,
            height = 500 - margin.top - margin.bottom,
            contextHeight = 50,
            contextWidth = width * .5;

        var svg = d3.select("#horizon_plot").append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", (height + margin.top + margin.bottom));

        d3.csv(data_file, createChart);

        // Create chart:
        function createChart(data){
          var activities_pre = [];
          var activities_post = [];
          var charts1 = [];
          var charts2 = [];
          var maxDataPoint = 0;

          // Load data and date numbers:
          var idate = 0;
          data.forEach(function(d) {
              idate = idate + 1;
              d.datenum = idate;
              d.date = +parse_date(parseDate(d.date));
              d.voice_pre = +d.voice_pre;
              d.voice_post = +d.voice_post;
              d.walk_pre = +d.walk_pre;
              d.walk_post = +d.walk_post;
              d.stand_pre = +d.stand_pre;
              d.stand_post = +d.stand_post;
              d.tap_pre = +d.tap_pre;
              d.tap_post = +d.tap_post;
          });
          //console.log(data[0].date);

          // Loop through first row and get each activity
          // and push odd columns into premed and even columns
          // into postmed activity arrays to use later
          var col = 0;
          for (var prop in data[0]) {
            if (data[0].hasOwnProperty(prop)) {
              if (prop != 'date') {
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
          var chartHeight = height * (1 / activitiesCount);

          // make sure these are all numbers, and identify
          // the maximum data point to set the Y-Axis scale
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
            //d.date = new Date(d.date,0,1);
          });
    
          for(var i = 0; i < activitiesCount; i++){
            charts1.push(new Chart({
                                  data: data.slice(),
                                  id: i,
                                  name: activities_post[i],
                                  width: width,
                                  height: height / activitiesCount,
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
                                  height: height / activitiesCount,
                                  maxDataPoint: maxDataPoint,
                                  svg: svg,
                                  margin: margin,
                                  showBottomAxis: (i == activities_post.length - 1)
                                }));
          }
    
          // Let's create the context brush that will let us zoom and pan the chart
          if (show_zoom == 1) {
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
                                    .x(function(d) { return contextXScale(d.datenum); })
                                    .y0(contextHeight)
                                    .y1(0);
            var brush = d3.svg.brush()
                              .x(contextXScale)
                              .on("brush", onBrush);
            var context = svg.append("g")
                              .attr("class","context")
                              .attr("transform", "translate(" + (margin.left + width * .25)
                              + "," + (height + margin.top + chartHeight) + ")");
      
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
              // this will return a date range to pass into the chart object
              var b = brush.empty() ? contextXScale.domain() : brush.extent();
              for(var i = 0; i < activitiesCount; i++){
                charts1[i].showOnly(b);
                charts2[i].showOnly(b);
              }
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

          // XScale
          this.xScale = d3.scale.linear()  // time.scale()
                  .range([0, this.width])
                  .domain(d3.extent(this.chartData.map(function(d) { return +d.datenum; })));

          // YScale is linear based on the maxData Point we found earlier
          this.yScale = d3.scale.linear()
                                .range([this.height,0])
                                .domain([0, max_value]); //this.maxDataPoint]);
          var xS = this.xScale;
          var yS = this.yScale;

          // create the chart (with interpolation):
          this.area = d3.svg.area()
                                .interpolate("linear")  //"cardinal")
                                .x(function(d) { return xS(d.datenum); })
                                .y0(this.height)
                                .y1(function(d) { return yS(d[localName]); });
          // create a mask (not required -- if not here, when we zoom/pan,
          // we'd see the chart go off to the left under the y-axis):
          this.svg.append("defs").append("clipPath")
                                  .attr("id", "clip-" + this.id)
                                  .append("rect")
                                    .attr("width", this.width)
                                    .attr("height", this.height);
          // Assign it a class so we can assign a fill color and position it on the page
          this.chartContainer = svg.append("g")
                  .attr('class',this.name.toLowerCase())
                  .attr("transform", "translate(" + this.margin.left + "," + 
                    (this.margin.top + (this.height * this.id) + (10 * this.id)) + ")");

          // We've created everything, let's actually add it to the page 
          this.chartContainer.append("path")
                              .data([this.chartData])
                              .attr("class", "horizon_plot")
                              .attr("clip-path", "url(#clip-" + this.id + ")")
                              .attr("d", this.area);

          // horizontal line to compare against:
          var shift_control_line = 40;
          var current_height = this.margin.top + (this.height * this.id) + (10 * this.id);
          var line_height = current_height + (1 - control_values[this.id]) * this.height;
          var myLine = svg.append("svg:line")
              .attr("x1", this.margin.left + shift_control_line)
              .attr("y1", line_height)
              .attr("x2", this.margin.left + width)
              .attr("y2", line_height)
              .style("stroke", "lightgray");

          // Enclosing box:
          /*
          rect = svg.append('svg:rect')
              .attr('width', width)
              .attr('height', height/4)
              .attr('x', margin.left)
              .attr('y', margin.top)
              .style("stroke", "black")
              .style("stroke-width", 1)
              .style("fill", "transparent");
          */

          // bottom axis on the last activity
          this.xAxisBottom = d3.svg.axis().scale(this.xScale).orient("bottom").ticks(31);
          if(this.showBottomAxis){
              this.chartContainer.append("g")
                  .attr("class", "x axis bottom")
                  .attr("transform", "translate(0," + (this.height + 11) + ")")
                  .call(this.xAxisBottom);
          }  
          this.yAxis = d3.svg.axis().scale(this.yScale).orient("left").ticks(1);

          this.chartContainer.append("g")
                              .attr("class", "y axis")
                              .attr("transform", "translate(-10,0)")
                              .call(this.yAxis);
          this.chartContainer.append("text")
                              .attr("class","activity-title")
                              .attr("transform", "translate(0,15)");
                              //.text(this.name);  // name from data header
        }
        Chart.prototype.showOnly = function(b){
            this.xScale.domain(b);
            this.chartContainer.select("path").data([this.chartData]).attr("d", this.area);
            this.chartContainer.select(".x.axis.bottom").call(this.xAxisBottom);
        }
    }
});
