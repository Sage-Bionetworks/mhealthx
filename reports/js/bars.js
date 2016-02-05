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
parseDate = d3.time.format("%Y-%b-%d").parse;
max_value = 1;        // maximum value for randomly generated data
empty_value = -1;     // negative value corresponding to missing data
control_voice = 0.85; // line to compare with control data
control_walk = 0.5;   // line to compare with control data
control_stand = 0.75; // line to compare with control data
control_tap = 0.68;   // line to compare with control data

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
//width = 870;
//height = 500;
bar_height = 80;
barchart_opacity = 0.75;
//margin = {top: 10, right: 40, bottom: 150, left: 60};
margin = {top: 0, right: 0, bottom: 0, left: 0};
width = 880 - margin.left - margin.right;
height = 500 - margin.top - margin.bottom;
xScale = d3.scale.ordinal()
    .rangeRoundBands([0, width], 0.05);
yScale = d3.scale.linear()
    .domain([0,max_value])
    .range([0,bar_height]);
xAxis = d3.svg.axis()
    .scale(xScale)
    .orient("bottom");
yAxis = d3.svg.axis()
    .scale(yScale)
    .orient("left")
    .ticks(10);

// Main function:
function drawGraphsForMonthlyData() {

    // Bar chart functions:
    barchart_voice_post();
    barchart_voice_pre();
    barchart_walk_post();
    barchart_walk_pre();
    barchart_stand_post();
    barchart_stand_pre();
    barchart_tap_post();
    barchart_tap_pre();


    //------------------------------------------------------------------------
    // Bar chart function for VOICE POST-med data:
    //------------------------------------------------------------------------
    function barchart_voice_post() {

      var svg = d3.select("#voice_post_bars").append("svg")
                  .attr("width", width)
                  .attr("height", height);

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
                  .attr("width", width)
                  .attr("height", height);

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
      });
    }

    //------------------------------------------------------------------------
    // Bar chart function for WALK POST-med data:
    //------------------------------------------------------------------------
    function barchart_walk_post() {

      var svg = d3.select("#walk_post_bars").append("svg")
                  .attr("width", width)
                  .attr("height", height);

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
                  .attr("width", width)
                  .attr("height", height);

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
        var line_height = (1 - control_voice) * height/4;
        var myLine = svg.append("svg:line")
            .attr("x1", 0)
            .attr("y1", line_height)
            .attr("x2", width)
            .attr("y2", line_height)
            .style("stroke", "lightgray");
      });
    }

    //------------------------------------------------------------------------
    // Bar chart function for STAND POST-med data:
    //------------------------------------------------------------------------
    function barchart_stand_post() {

      var svg = d3.select("#stand_post_bars").append("svg")
                  .attr("width", width)
                  .attr("height", height);

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
                  .attr("width", width)
                  .attr("height", height);

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
        var line_height = (1 - control_voice) * height/4;
        var myLine = svg.append("svg:line")
            .attr("x1", 0)
            .attr("y1", line_height)
            .attr("x2", width)
            .attr("y2", line_height)
            .style("stroke", "lightgray");
      });
    }

    //------------------------------------------------------------------------
    // Bar chart function for TAP POST-med data:
    //------------------------------------------------------------------------
    function barchart_tap_post() {

      var svg = d3.select("#tap_post_bars").append("svg")
                  .attr("width", width)
                  .attr("height", height);

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
                    .attr("height", height + margin.top + margin.bottom);
  
        // Load data:
        var idate = 0;
        d3.csv(data_file, function (error, data) {

            data.forEach(function (d) {
                idate = idate + 1;
                d.date = parseDate(d.date);
                d.datenum = idate;
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


            // axes:
//            xScale = d3.time.scale()
            //    .domain(data.map(function (d) { return parseDate(d.date); }));
            xScale.domain(data.map(function (d) { return d.date; }));
//            xScale = d3.time.scale()
//              .domain(d3.extent(data.map(function(d) { return d.datenum; })));
/*
            bars
              .append("g")
              .attr("class", "x axis")
              .attr("transform", "translate(0,10)")
              .call(xAxis);
            bars
              .append("g")
              .attr("class", "y axis")
              .attr("transform", "translate(-10,0)")
              .call(yAxis);


margin = {top: 10, right: 40, bottom: 150, left: 60};
width = 980 - margin.left - margin.right;
height = 500 - margin.top - margin.bottom;

*/

            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis)
                .append("text")
                .attr("transform", "rotate(0)")
                .attr("y", 22)
                .attr("x", 3)
                .attr("dy", ".71em")
                .style("text-anchor", "bottom")
                .text("Timeline");
            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis)
                .append("text")
//                .attr("transform", "rotate(0)")
                .attr("y", -15)
                .attr("x", -25)
//                .attr("dy", ".71em")
//                .style("text-anchor", "top")
                .text("YAXIS");

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

            svg.select("g.x").call(xAxis);
            svg.select("g.y").call(yAxis);

            // horizontal line to compare against:
            var line_height = (1 - control_voice) * height/4;
            var myLine = svg.append("svg:line")
                .attr("x1", 0)
                .attr("y1", line_height)
                .attr("x2", width)
                .attr("y2", line_height)
                .style("stroke", "lightgray");


      });
    }

}

drawGraphsForMonthlyData();
