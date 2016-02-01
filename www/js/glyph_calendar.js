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
    dates = [27,3,10,17,24,28,4,11,18,25,29,5,12,19,26,30,6,13,20,27,31,7,14,21,28,
             1,8,15,22,29,2,9,16,23,30];
            //[27,28,29,30,31,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
            // 16,17,18,19,20,21,22,23,24,25,26,27,28,29,30];

    // Generate random data:
    data = getDataForMonth(number_of_sides * number_of_bars, max_value, empty_value);

    // Create a radial barchart glyph for each date:
    for (var i = 0; i < 5; i++) {
        for (var j = 0; j < 7; j++) {
            var date = dates[j*5 + i];
            var rbars = radial_bars(data[i*7 + j],
                                    number_of_bars, cap_value, empty_value, date);
        }
    }

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

    };
};

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
