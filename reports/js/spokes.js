// This JavaScript D3 program generates an mPower performance report
// from mPower Parkinson mobile health data (parkinsonmpower.org.
// Github repository: http://sage-bionetworks.github.io/mhealthx/
//
// Authors:
//  - Arno Klein, 2016  (arno@sagebase.org)  http://binarybottle.com
//
// Copyright 2016, Sage Bionetworks (sagebase.org), Apache v2.0 License
//------------------------------------------------------------------------

//------------------------------------------------------------------------
// Settings
//------------------------------------------------------------------------
max_value = 1;        // maximum value
cap_value = 0.9;      // maximum value visualized (full extent of cell)
empty_value = -1;     // negative value corresponding to missing data
control_voice = 0.85; // line to compare with control data
control_walk = 0.5;   // line to compare with control data
control_stand = 0.75; // line to compare with control data
control_tap = 0.68;   // line to compare with control data
control_values = [control_voice, control_walk, control_stand, control_tap]
// Number of bars per bar chart (2 for pre-/post-medication),
// each extending from the side of a square (4 sides for 4 activities):
number_of_bars = 2;   // CURRENTLY FIXED

// Background colors:
background_color = "#e2e2e2";  // color of circle behind radial bar chart
empty_color = "#ffffff";       // color of background and empty data
// Pairs of colors for 4 directions (pre-/post-medication for mPower's 4 activities):
walk_pre_color = "#20AED8";
walk_post_color = "#2C1EA2";
stand_pre_color = "#6E6E6E";
stand_post_color = "#151515";
voice_pre_color = "#EEBE32";
voice_post_color = "#9F5B0D";
tap_pre_color = "#F78181";
tap_post_color = "#C02504";
left_colors = [walk_pre_color, walk_post_color];
right_colors = [stand_pre_color, stand_post_color];
up_colors = [voice_pre_color, voice_post_color];
down_colors = [tap_pre_color, tap_post_color];

// Data:
data_file = './data.txt';
parseDate = d3.time.format("%Y-%b-%d").parse;
parse_year = d3.time.format("%Y");
parse_month = d3.time.format("%B");
parse_weekdaynumber = d3.time.format("%w");
parse_date = d3.time.format("%d");

//------------------------------------------------------------------------
// Load data
//------------------------------------------------------------------------
d3.csv(data_file, function(error, data) {

    var left_data_pre = [];
    var left_data_post = [];
    var right_data_pre = [];
    var right_data_post = [];
    var up_data_pre = [];
    var up_data_post = [];
    var down_data_pre = [];
    var down_data_post = [];
    var idata = 0;
    data.forEach(function (d) {

        // enforce numbers and extract date strings:
        d.year = parse_year(parseDate(d.date));
        d.month = parse_month(parseDate(d.date));
        d.weekdaynumber = parse_weekdaynumber(parseDate(d.date));
        d.date = +parse_date(parseDate(d.date));
        d.voice_pre = +d.voice_pre;
        d.voice_post = +d.voice_post;
        d.walk_pre = +d.walk_pre;
        d.walk_post = +d.walk_post;
        d.stand_pre = +d.stand_pre;
        d.stand_post = +d.stand_post;
        d.tap_pre = +d.tap_pre;
        d.tap_post = +d.tap_post;

        // group into arrays:
        left_data_pre[idata] = d.walk_pre;
        right_data_pre[idata] = d.stand_pre;
        up_data_pre[idata] = d.voice_pre;
        down_data_pre[idata] = d.tap_pre;
        left_data_post[idata] = d.walk_post;
        right_data_post[idata] = d.stand_post;
        up_data_post[idata] = d.voice_post;
        down_data_post[idata] = d.tap_post;
        idata = idata + 1;
    });
    //console.log(daynumber(data[0].date));
    var lendata = data.length;
    var middate = Math.round(lendata/2);
    document.getElementById("month").innerHTML = data[middate].month;
    document.getElementById("year").innerHTML = data[middate].year;
    n_empty_cells = data[0].weekdaynumber;

    //--------------------------------------------------------------------
    // Radial bar charts
    //--------------------------------------------------------------------
    // Empty cells:
    var count = 0;
    for (var j = 0; j < 7; j++) {
        if (count < n_empty_cells) {
            radial_bars([],[],[],[], '', 1);
        }
        count = count + 1;
    }
    // Occupied cells:
    var count = 0;
    for (var i = 0; i < 5; i++) {
        for (var j = 0; j < 7; j++) {
            if (count < lendata) {
                var idata = i*7 + j;
                var left_pre = left_data_pre[idata];
                var right_pre = right_data_pre[idata];
                var up_pre = up_data_pre[idata];
                var down_pre = down_data_pre[idata];
                var left_post = left_data_post[idata];
                var right_post = right_data_post[idata];
                var up_post = up_data_post[idata];
                var down_post = down_data_post[idata];
                var date = data[idata].date;
                radial_bars([left_pre, left_post],
                            [right_pre, right_post],
                            [up_pre, up_post],
                            [down_pre, down_post],
                            date, 0);
            }
            count = count + 1;
        }
    }

    //--------------------------------------------------------------------
    // Radial barchart function
    //--------------------------------------------------------------------
    function radial_bars(left_data, right_data, up_data, down_data,
                         date, is_empty_cell) { 

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
        translate_y = function(d, index){ 
            return total_width/2 + plot_y(index) - bar_width; };
        translate_x = function(d, i) { 
            return "translate(" + (bar_length + i * bar_width) + ", 0)"; };

        // Glyph:
        glyph_calendar = d3.select('#glyph_calendar')
        glyph = glyph_calendar.append('svg')
            .attr('height', total_width)
            .attr('width', total_width)

        // Skip empty cells:
        if (is_empty_cell == 0 ) {

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

            // Date text:
            text = glyph.append('text')
                .attr('x', 4)
                .attr('y', 16)
                .style('fill', 'black')
                .style('font-size', '9pt')
                .text(date)

            var square_color = '#aaaaaa';
        } else {
            var square_color = empty_color;
        }

        // Enclosing square:
        rect = glyph.append('rect')
            .attr('width', total_width)
            .attr('height', total_width)
            .attr('x', 0)
            .attr('y', 0)
            .style("stroke", square_color)
            .style("stroke-width", 1)
            .style("fill", 'transparent');
    }
});
