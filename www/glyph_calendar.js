// This JavaScript program uses D3 to generate radial barchart glyphs
// in the cells of a monthly calendar.

//----------------------------------------------------------------------------
// DATA
//----------------------------------------------------------------------------
// Generate a list of number_of_values random numbers with maximum value max_number:
var randomNumbers = function(number_of_values, max_number) { 
    var numbers = [];
    for (var i = 0; i < number_of_values; i++) {
        numbers.push(parseInt(Math.random() * max_number));
    }
    return numbers;
};
// Generate 35 lists of random numbers for the days of a month:
function getDataForMonth(number_of_values, max_number) {
    var randomData = [];
    for (var i = 0; i < 35; i++) {
        randomData.push(randomNumbers(number_of_values, max_number));
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

    // Get data for a month:
    // Number of bars per bar chart (2 for pre-/post-medication),
    // each extending from the side of a square (4 sides for 4 activities),
    // with a maximum display value of max_number, centered within a calendar cell:
    var number_of_sides = 4; // CURRENTLY FIXED
    var number_of_bars = 2;  // CURRENTLY FIXED
    var max_number = 20;
    var data = getDataForMonth(number_of_sides * number_of_bars, max_number);


    // Create radial barchart glyphs:
    var dates = [27,28,29,30,31,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30];

    for (i = 0; i < 5; i++) {
        for (j = 0; j < 7; j++) {
            var shade = 0;
            if (i == 0) {
                if (j < 5) {
                    shade = 1;
                }
            }
            date = dates[j*5 + i]
            var rbars = radial_bars(data[i*7 + j], number_of_bars, max_number, date, shade);
        }
    }

    //--------------------------------------------------------------------
    // Radial barchart function
    //--------------------------------------------------------------------
    function radial_bars(data, number_of_bars, max_number, date, shade) { 

        // Data broken up into pairs for each of four directions
        // (pre-/post-med for voice, stand, tap, and walk activities):
        var leftData = [data[0], data[1]];
        var rightData = [data[2], data[3]];
        var upData = [data[4], data[5]];
        var downData = [data[6], data[7]];

        // Colors broken up into pairs for each of four directions
        // (pre-/post-med for voice, stand, tap, and walk activities):
        colors = ["#EEBE32", "#9F5B0D", "#B0A9B7", "#6F6975", "#EB7D65", "#C02504", "#20AED8", "#2C1EA2"];
        var leftColors = [colors[0], colors[1]];
        var rightColors = [colors[2], colors[3]];
        var upColors = [colors[4], colors[5]];
        var downColors = [colors[6], colors[7]];
        if (shade == 0) {
            fill_shade1 = "#ffffff";
            fill_shade2 = "#ffffff";
        } else {
            fill_shade1 = "#F2F2F2";
            fill_shade2 = "#ffffff";
        }

        // Plot dimensions
        var bar_width = 15,
            bar_length = 50,
            left_origin = bar_length,
            barplot_width = number_of_bars * bar_width,
            total_width = barplot_width + 2 * bar_length,
            total_width_neg = bar_length - total_width;
        var value2length = d3.scale.linear()
           .domain([0, max_number])
           .range([0, bar_length]);
        var y = d3.scale.linear()
           .domain([0, number_of_bars])
           .range([0, barplot_width]);
        var translate_y = function(d, index){ return total_width/2 + y(index) - bar_width; } 

        // Glyph:
        chart = d3.select('#chart')
        glyph = chart.append('svg')
            .attr('height', total_width)
            .attr('width', total_width)

        // Enclosing square:
        rect = glyph.append('rect')
            .attr('width', total_width)
            .attr('height', total_width)
            .attr('x', 0)
            .attr('y', 0)
            .style("stroke", "#aaaaaa")
            .style("stroke-width", 1)
            .style("fill", fill_shade1);

        // Date text:
        text = glyph.append('text')
//            .data(dates)
//          .enter().append("dates")
            .attr('x', 5)
            .attr('y', 15)
            .style('fill', 'black')
            .text(function(d, i) { return dates[i]; })

        // Enclosing circle:
        glyph.selectAll("rect.circle")
            .data(leftData)
          .enter().append("circle")
            .attr("cx", total_width/2)
            .attr("cy", total_width/2)
            .attr("r", total_width/2)
            .style("stroke", "#aaaaaa")
            .style("stroke-width", 0.5)
            .style("fill", fill_shade2);

        // Position LEFT data
        glyph.selectAll("rect.left")
            .data(leftData)
          .enter().append("rect")
            .attr("x", function(pos) { return left_origin - value2length(pos); })
            .attr("y", translate_y)
            .attr("width", value2length)
            .attr("height", bar_width)
            .style("fill", function(d, i) { return leftColors[i]; })
            .attr("class", "left");

        // Position RIGHT data
        glyph.selectAll("rect.right")
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
        glyph.selectAll("rect.up")
            .data(upData)
          .enter().append("rect")
            .attr("transform", translate_x)
            .attr("y", function(pos) { return total_width/2 - value2length(pos) - bar_width; })
            .attr("height", value2length)
            .attr("width", bar_width - 1)
            .style("fill", function(d, i) { return upColors[i]; })
            .attr("class", "up");

        // Position DOWN data
        glyph.selectAll("rect.down")
            .data(downData)
          .enter().append("rect")
            .attr("transform", translate_x)
            .attr("y", total_width/2 + bar_width)
            .attr("height", value2length)
            .attr("width", bar_width)
            .style("fill", function(d, i) { return downColors[i]; })
            .attr("class", "down");
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
