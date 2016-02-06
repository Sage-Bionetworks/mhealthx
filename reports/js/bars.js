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

// Data settings:
data_file = './data.txt';
max_value = 1;        // maximum value for randomly generated data
empty_value = -1;     // negative value corresponding to missing data
control_voice = 0.85; // line to compare with control data
control_walk = 0.5;   // line to compare with control data
control_stand = 0.75; // line to compare with control data
control_tap = 0.68;   // line to compare with control data
parseDate = d3.time.format("%Y-%b-%d").parse;
parse_year = d3.time.format("%Y");
parse_month = d3.time.format("%B");

// Color settings:
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

// Bar chart settings:
bar_height = 80;
barchart_opacity = 0.75;
//margin = {top: 10, right: 40, bottom: 150, left: 60};
margin = {top: 10, right: 40, bottom: 150, left: 60},
width = 980 - margin.left - margin.right,
height = 500 - margin.top - margin.bottom,
yScale = d3.scale.linear()
    .domain([0,max_value])
    .range([0,bar_height]);

// Main function:
d3.csv(data_file, function(error, data) {

    // Bar chart functions:
    barchart_voice_post();
    barchart_voice_pre();
    barchart_walk_post();
    barchart_walk_pre();
    barchart_stand_post();
    barchart_stand_pre();
    barchart_tap_post();
    barchart_tap_pre();

    // Add month and year to the top of the graphic:
    data.forEach(function(d) {
        d.year = parse_year(parseDate(d.date));
        d.month = parse_month(parseDate(d.date));
    });
    var middate = Math.round(data.length/2);
    month_name = data[middate].month;
    document.getElementById("month").innerHTML = month_name;
    document.getElementById("year").innerHTML = data[middate].year;

    //------------------------------------------------------------------------
    // Bar chart function for VOICE POST-med data:
    //------------------------------------------------------------------------
    function barchart_voice_post() {

      var svg = d3.select("#voice_post_bars").append("svg")
                  .attr("width", width + margin.left + margin.right)
                  .attr("height", (height + margin.top + margin.bottom));

      // Load data:
      d3.csv(data_file, function (error, data) {

        // Create the chart:
        bars = svg.selectAll("rect")
          .data(data)
          .enter().append("rect")
          .attr("x", function(d, i) {return i * (width / data.length);})
            .attr("y", function(d){return bar_height - yScale(d.voice_post);})
          .attr("width", width / data.length)
          .attr("height", function(d) {return yScale(d.voice_post);})
          .attr("fill", voice_post_color);
      });
    }

    //------------------------------------------------------------------------
    // Bar chart function for VOICE PRE-med data:
    //------------------------------------------------------------------------
    function barchart_voice_pre() {

      var svg = d3.select("#voice_pre_bars").append("svg")
                  .attr("width", width + margin.left + margin.right)
                  .attr("height", (height + margin.top + margin.bottom));

      // Load data:
      d3.csv(data_file, function (error, data) {

        bars = svg.selectAll("rect")
          .data(data)
          .enter().append("rect")
          .attr("x", function(d, i) {return i * (width / data.length);})
            .attr("y", function(d){return bar_height - yScale(d.voice_pre);})
          .attr("width", width / data.length)
          .attr("height", function(d) {return yScale(d.voice_pre);})
          .attr("fill", voice_pre_color)
          .style("opacity", barchart_opacity);

        // horizontal line to compare against:
        var line_height = (1 - control_voice) * height/4;
        var myLine = svg.append("svg:line")
            .attr("x1", 0)
            .attr("y1", line_height)
            .attr("x2", width)
            .attr("y2", line_height)
            .style("stroke", "lightgray");

        // Enclosing box:
        rect = svg.append('rect')
            .attr('width', width)
            .attr('height', height/4 - 5)
            .attr('x', 0)
            .attr('y', 0)
            .style("stroke", "black")
            .style("stroke-width", 1)
            .style("fill", "transparent");

      });
    }

    //------------------------------------------------------------------------
    // Bar chart function for WALK POST-med data:
    //------------------------------------------------------------------------
    function barchart_walk_post() {

      var svg = d3.select("#walk_post_bars").append("svg")
                  .attr("width", width + margin.left + margin.right)
                  .attr("height", (height + margin.top + margin.bottom));

      // Load data:
      d3.csv(data_file, function (error, data) {

        // Create the chart:
        bars = svg.selectAll("rect")
          .data(data)
          .enter().append("rect")
          .attr("x", function(d, i) {return i * (width / data.length);})
            .attr("y", function(d){return bar_height - yScale(d.walk_post);})
          .attr("width", width / data.length)
          .attr("height", function(d) {return yScale(d.walk_post);})
          .attr("fill", walk_post_color);
      });
    }

    //------------------------------------------------------------------------
    // Bar chart function for WALK PRE-med data:
    //------------------------------------------------------------------------
    function barchart_walk_pre() {

      var svg = d3.select("#walk_pre_bars").append("svg")
                  .attr("width", width + margin.left + margin.right)
                  .attr("height", (height + margin.top + margin.bottom));

      // Load data:
      d3.csv(data_file, function (error, data) {

        bars = svg.selectAll("rect")
          .data(data)
          .enter().append("rect")
          .attr("x", function(d, i) {return i * (width / data.length);})
            .attr("y", function(d){return bar_height - yScale(d.walk_pre);})
          .attr("width", width / data.length)
          .attr("height", function(d) {return yScale(d.walk_pre);})
          .attr("fill", walk_pre_color)
          .style("opacity", barchart_opacity);

        // horizontal line to compare against:
        var line_height = (1 - control_walk) * height/4;
        var myLine = svg.append("svg:line")
            .attr("x1", 0)
            .attr("y1", line_height)
            .attr("x2", width)
            .attr("y2", line_height)
            .style("stroke", "lightgray");

        // Enclosing box:
        rect = svg.append('rect')
            .attr('width', width)
            .attr('height', height/4 - 5)
            .attr('x', 0)
            .attr('y', 0)
            .style("stroke", "black")
            .style("stroke-width", 1)
            .style("fill", "transparent");

      });
    }

    //------------------------------------------------------------------------
    // Bar chart function for STAND POST-med data:
    //------------------------------------------------------------------------
    function barchart_stand_post() {

      var svg = d3.select("#stand_post_bars").append("svg")
                  .attr("width", width + margin.left + margin.right)
                  .attr("height", (height + margin.top + margin.bottom));

      // Load data:
      d3.csv(data_file, function (error, data) {

        // Create the chart:
        bars = svg.selectAll("rect")
          .data(data)
          .enter().append("rect")
          .attr("x", function(d, i) {return i * (width / data.length);})
            .attr("y", function(d){return bar_height - yScale(d.stand_post);})
          .attr("width", width / data.length)
          .attr("height", function(d) {return yScale(d.stand_post);})
          .attr("fill", stand_post_color);
      });
    }

    //------------------------------------------------------------------------
    // Bar chart function for STAND PRE-med data:
    //------------------------------------------------------------------------
    function barchart_stand_pre() {

      var svg = d3.select("#stand_pre_bars").append("svg")
                  .attr("width", width + margin.left + margin.right)
                  .attr("height", (height + margin.top + margin.bottom));

      // Load data:
      d3.csv(data_file, function (error, data) {

        bars = svg.selectAll("rect")
          .data(data)
          .enter().append("rect")
          .attr("x", function(d, i) {return i * (width / data.length);})
            .attr("y", function(d){return bar_height - yScale(d.stand_pre);})
          .attr("width", width / data.length)
          .attr("height", function(d) {return yScale(d.stand_pre);})
          .attr("fill", stand_pre_color)
          .style("opacity", barchart_opacity);

        // horizontal line to compare against:
        var line_height = (1 - control_stand) * height/4;
        var myLine = svg.append("svg:line")
            .attr("x1", 0)
            .attr("y1", line_height)
            .attr("x2", width)
            .attr("y2", line_height)
            .style("stroke", "lightgray");

        // Enclosing box:
        rect = svg.append('rect')
            .attr('width', width)
            .attr('height', height/4 - 5)
            .attr('x', 0)
            .attr('y', 0)
            .style("stroke", "black")
            .style("stroke-width", 1)
            .style("fill", "transparent");

      });
    }

    //------------------------------------------------------------------------
    // Bar chart function for TAP POST-med data:
    //------------------------------------------------------------------------
    function barchart_tap_post() {

      var svg = d3.select("#tap_post_bars").append("svg")
                  .attr("width", width + margin.left + margin.right)
                  .attr("height", (height + margin.top + margin.bottom));

      // Load data:
      d3.csv(data_file, function (error, data) {

        // Create the chart:
        bars = svg.selectAll("rect")
          .data(data)
          .enter().append("rect")
          .attr("x", function(d, i) {return i * (width / data.length);})
            .attr("y", function(d){return bar_height - yScale(d.tap_post);})
          .attr("width", width / data.length)
          .attr("height", function(d) {return yScale(d.tap_post);})
          .attr("fill", tap_post_color);

      });
    }

    //------------------------------------------------------------------------
    // Bar chart function for TAP PRE-med data:
    //------------------------------------------------------------------------
    function barchart_tap_pre() {

        var svg = d3.select("#tap_pre_bars").append("svg")
                  .attr("width", width + margin.left + margin.right)
                  .attr("height", (height + margin.top + margin.bottom));
  
        // Load data:
        var idate = 0;
        d3.csv(data_file, function (error, data) {

            // axes:
            data.forEach(function (d) {
                idate = idate + 1;
                d.date = parseDate(d.date);
                d.datenum = idate;
            });
            xScale = d3.scale.linear()  // time.scale()
                .range([0, width])
                .domain([0, idate]);  //data.map(function (d) { return +d.datenum; }));
            xAxis = d3.svg.axis().scale(xScale).orient("bottom").ticks(31);
                //.attr("transform", "translate(-5,0)");

            yAxis = d3.svg.axis()
                .scale(yScale)
                .orient("left")
                .ticks(1);
            svg.append("g")
              .attr("class", "x axis")
              .attr("transform", "translate(0,80)")
              .call(xAxis);
            svg.append("g")
              .attr("class", "y axis")
              .attr("transform", "translate(-10,0)")
              .call(yAxis);
            svg.select("g.x").call(xAxis);
            svg.select("g.y").call(yAxis);

            svg.selectAll(".bar")
                .data(data)
                .enter().append("rect")
                .attr("class", "bar")
                .attr("x", function(d, i) {return i * (width / data.length);})
                .attr("y", function(d){return bar_height - yScale(d.tap_pre);})
                .attr("width", width / data.length)
                .attr("height", function(d) {return yScale(d.tap_pre);})
                .attr("fill", tap_pre_color)
                .style("opacity", barchart_opacity);

            // horizontal line to compare against:
            var line_height = (1 - control_tap) * height/4;
            var myLine = svg.append("svg:line")
                .attr("x1", 0)
                .attr("y1", line_height)
                .attr("x2", width)
                .attr("y2", line_height)
                .style("stroke", "lightgray");

            // Enclosing box:
            rect = svg.append('rect')
                .attr('width', width)
                .attr('height', height/4 - 5)
                .attr('x', 0)
                .attr('y', 0)
                .style("stroke", "black")
                .style("stroke-width", 1)
                .style("fill", "transparent");

            // axis labels:
            document.getElementById("xaxis_label").innerHTML = "day in " + month_name;
            document.getElementById("yaxis_label1").innerHTML = max_value;
            document.getElementById("yaxis_label2").innerHTML = "0";
            document.getElementById("yaxis_label3").innerHTML = max_value;
            document.getElementById("yaxis_label4").innerHTML = "0";
            document.getElementById("yaxis_label5").innerHTML = max_value;
            document.getElementById("yaxis_label6").innerHTML = "0";
            document.getElementById("yaxis_label7").innerHTML = max_value;
            document.getElementById("yaxis_label8").innerHTML = "0";

      });
    }
});