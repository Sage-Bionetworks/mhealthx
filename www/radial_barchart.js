// Random data
var number_of_bars = 10;
var max_number = 20;
var randomNumbers = function() { 
    var numbers = [];
    var colors = [];
    for (var i = 0; i < number_of_bars; i++) {
        numbers.push(parseInt(Math.random() * max_number));
        colors.push(d3.scale.category20(parseInt(Math.random() * max_number)));
    }
    return [numbers, colors];
};
var leftData = randomNumbers();
var rightData = randomNumbers();
var upData = randomNumbers();
var downData = randomNumbers();

// Plot dimensions
var chart,
    bar_width = 20,
    bar_length = 100,
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
    .data(leftData[0])
  .enter().append("rect")
    .attr("x", function(pos) { return left_origin - value2length(pos); })
    .attr("y", translate_y)
    .attr("width", value2length)
    .attr("height", bar_width)
    .style("fill", leftData[1])
    .attr("class", "left");

// Position RIGHT data
chart.selectAll("rect.right")
    .data(rightData[0])
  .enter().append("rect")
    .attr("x", left_origin + barplot_width)
    .attr("y", translate_y)
    .attr("width", value2length)
    .attr("height", bar_width) 
//          .style("fill", function(d, i) { return index2color(i); })
    .attr("class", "right");

// Position UP data
var translate_x = function(d, i) { return "translate(" + (left_origin + i * bar_width) + ", 0)"; }
chart.selectAll("rect.up")
    .data(upData[0])
  .enter().append("rect")
    .attr("transform", translate_x)
    .attr("y", function(pos) { return top_offset - value2length(pos); })
    .attr("height", value2length)
    .attr("width", bar_width - 1)
//          .style("fill", function(d, i) { return index2color(i); })
    .attr("class", "up");

// Position DOWN data
chart.selectAll("rect.down")
    .data(downData[0])
  .enter().append("rect")
    .attr("transform", translate_x)
    .attr("y", top_offset + barplot_width)
    .attr("height", value2length)
    .attr("width", bar_width)
//          .style("fill", function(d, i) { return index2color(i); })
    .attr("class", "down");


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
