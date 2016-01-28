// Random data
var number_of_sides = 4; // FIXED
var number_of_bars = 2; // FIXED
var number_of_values = number_of_sides * number_of_bars;
var max_number = 20;
// Pre/post-med for voice, stand, tap, and walk:
var color_list = ["#EEBE32", "#9F5B0D", "#B0A9B7", "#6F6975", "#EB7D65", "#C02504", "#20AED8", "#2C1EA2"];
var randomNumbers = function(number_of_values, max_number) { 
    var numbers = [];
    for (var i = 0; i < number_of_values; i++) {
        numbers.push(parseInt(Math.random() * max_number));
    }
    return numbers;
};
var randomColors = function(number_of_values, color_list) { 
    var colors = [];
    for (var i = 0; i < number_of_values; i++) {
        colors.push(color_list[i]);
    }
    return colors;
};
var values = randomNumbers(number_of_values, max_number);
var colors = randomColors(number_of_values, color_list);
var leftData = [values[0], values[1]];
var rightData = [values[2], values[3]];
var upData = [values[4], values[5]];
var downData = [values[6], values[7]];
var leftColors = [colors[0], colors[1]];
var rightColors = [colors[2], colors[3]];
var upColors = [colors[4], colors[5]];
var downColors = [colors[6], colors[7]];

// Plot dimensions
var chart,
    glyph_size = 160;
    bar_width = 15,
    bar_length = glyph_size / 2 - 2 * bar_width,
    right_offset = 100,
    left_origin = right_offset + bar_length
    top_offset = 120;
    barplot_width = number_of_bars * bar_width,
    total_width = barplot_width + 2 * bar_length
var chart = d3.select("body")
  .append('svg')
    .attr('class', 'chart')
    .attr('width', right_offset + total_width)
    .attr('height', top_offset + total_width);
var value2length = d3.scale.linear()
   .domain([0, max_number])
   .range([0, bar_length]);
var y = d3.scale.linear()
   .domain([0, number_of_bars])
   .range([0, barplot_width]);
var translate_y = function(d, index){ return top_offset + y(index); } 

// Position LEFT data
chart.selectAll("rect.left")
    .data(leftData)
  .enter().append("rect")
    .attr("x", function(pos) { return left_origin - value2length(pos); })
    .attr("y", translate_y)
    .attr("width", value2length)
    .attr("height", bar_width)
    .style("fill", function(d, i) { return leftColors[i]; })
    .attr("class", "left");

// Position RIGHT data
chart.selectAll("rect.right")
    .data(rightData)
  .enter().append("rect")
    .attr("x", left_origin + barplot_width)
    .attr("y", translate_y)
    .attr("width", value2length)
    .attr("height", bar_width) 
    .style("fill", function(d, i) { return rightColors[i]; })
    .attr("class", "right");

// Position UP data
var translate_x = function(d, i) { return "translate(" + (left_origin + i * bar_width) + ", 0)"; }
chart.selectAll("rect.up")
    .data(upData)
  .enter().append("rect")
    .attr("transform", translate_x)
    .attr("y", function(pos) { return top_offset - value2length(pos); })
    .attr("height", value2length)
    .attr("width", bar_width - 1)
    .style("fill", function(d, i) { return upColors[i]; })
    .attr("class", "up");

// Position DOWN data
chart.selectAll("rect.down")
    .data(downData)
  .enter().append("rect")
    .attr("transform", translate_x)
    .attr("y", top_offset + barplot_width)
    .attr("height", value2length)
    .attr("width", bar_width)
    .style("fill", function(d, i) { return downColors[i]; })
    .attr("class", "down");


/*
// Text (numbers on bars) for left data
chart.selectAll("text.leftscore")
    .data(leftData[0])
  .enter().append("text")
    .attr("x", function(pos) { return left_origin - value2length(pos); })
    .attr("y", translate_y)
    .attr("dx", "1.2em")
    .attr("dy", bar_width - 3)
    .attr("text-anchor", "end")
    .attr('class', 'leftscore')
    .text(String);
// Text (numbers on bars) for right data
chart.selectAll("text.score")
    .data(rightData[0])
  .enter().append("text")
    .attr("x", function(pos) { return left_origin + barplot_width + value2length(pos); })
    .attr("y", translate_y)
    .attr("dx", "-.36em")
    .attr("dy", bar_width - 3)
    .attr("text-anchor", "end")
    .attr('class', 'score')
    .text(String);
*/
