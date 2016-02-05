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
width = 130;  // calendar cell width;
height = width;
weight = 1/8;

// Plot dimensions:
radius = Math.min(width, height) / 2;  // maximum radius (in pixels)
innerRadius = 0;

// Background colors:
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

    data.forEach(function (d) {
        d.year = parse_year(parseDate(d.date));
        d.month = parse_month(parseDate(d.date));
        d.weekdaynumber = parse_weekdaynumber(parseDate(d.date));
        d.date = +parse_date(parseDate(d.date));
        var colors = [];
        if (+d.voice_pre==-1) { colors[0] = empty_color; } else { colors[0] = voice_pre_color; }
        if (+d.voice_post==-1) { colors[1] = empty_color; } else { colors[1] = voice_post_color; }
        if (+d.walk_post==-1) { colors[2] = empty_color; } else { colors[2] = walk_post_color; }
        if (+d.walk_pre==-1) { colors[3] = empty_color; } else { colors[3] = walk_pre_color; }
        if (+d.stand_post==-1) { colors[4] = empty_color; } else { colors[4] = stand_post_color; }
        if (+d.stand_pre==-1) { colors[5] = empty_color; } else { colors[5] = stand_pre_color; }
        if (+d.tap_pre==-1) { colors[6] = empty_color; } else { colors[6] = tap_pre_color; }
        if (+d.tap_post==-1) { colors[7] = empty_color; } else { colors[7] = tap_post_color; }
        d.colors = colors;
        d.values = [1,1,1,1,1,1,1,1];
    });
    //console.log(daynumber(data[0].date));
    var lendata = data.length;
    var middate = Math.round(lendata/2);
    document.getElementById("month").innerHTML = data[middate].month;
    document.getElementById("year").innerHTML = data[middate].year;
    n_empty_cells = data[0].weekdaynumber;

    //--------------------------------------------------------------------
    // Pie charts
    //--------------------------------------------------------------------
    // Empty cells:
    var count = 0;
    for (var j = 0; j < 7; j++) {
        if (count < n_empty_cells) { 
            pie_charts([], [], '', 1);
        }
        count = count + 1;
    }
    // Occupied cells:
    var count = 0;
    for (var i = 0; i < 5; i++) {
        for (var j = 0; j < 7; j++) {
            if (count < lendata) {
                var idata = i*7 + j;
                var date = data[idata].date;
                pie_charts(data[idata].values, data[idata].colors, date, 0);
            }
            count = count + 1;
        }
    }

    //--------------------------------------------------------------------
    // Pie chart function
    //--------------------------------------------------------------------
    function pie_charts(data_values, data_colors, date, is_empty_cell) { 

        var svg = d3.select('#glyph_calendar')
                    .append('svg')
                        .attr('width', width)
                        .attr('height', height)
                    .append('g')
                        .attr('transform', 'translate(' + (width / 2) + 
                          ',' + (height / 2) + ')');

        if (is_empty_cell == 0) {
            var arc = d3.svg.arc().outerRadius(radius);

            var pie = d3.layout.pie()
              .value(function(d, i) { return data_values[i]; });

            var path = svg.selectAll('path')
              .data(pie(data_values))
              .enter()
              .append('path')
              .attr('d', arc)
              .attr('fill', function(d, i) { return data_colors[i]; });

            // Date text:
            text = svg.append('text')
                .attr('x', 4 - radius)
                .attr('y', 16 - radius)
                .style('fill', 'black')
                .style('font-size', '9pt')
                .text(date);

            var square_color = '#aaaaaa';
        } else { 
            var square_color = empty_color;
        }

        // Enclosing square:
        rect = svg.append('rect')
            .attr('width', width)
            .attr('height', height)
            .attr('x', -radius)
            .attr('y', -radius)
            .style("stroke", square_color)
            .style("stroke-width", 1)
            .style("fill", "transparent");
    }
});
