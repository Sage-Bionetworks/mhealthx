// This JavaScript program uses D3 to generate radial barchart glyphs
// in the cells of a monthly calendar.


//----------------------------------------------------------------------------
// Graph glyphs within a calendar
//----------------------------------------------------------------------------
function drawGraphsForMonthlyData() {

    //------------------------------------------------------------------------
    // Radial barcharts
    //------------------------------------------------------------------------
    var pies = 0;
    if (pies == 0) {

        // Get data for a month:
        // Number of bars per bar chart (2 for pre-/post-medication),
        // each extending from the side of a square (4 sides for 4 activities),
        // with a maximum display value of max_number, centered within a calendar cell:
        var number_of_sides = 4; // CURRENTLY FIXED
        var number_of_bars = 2;  // CURRENTLY FIXED
        var number_of_values = number_of_sides * number_of_bars;
        var max_number = 20;
        var data = getDataForMonth(number_of_values, max_number);
        var leftData = [data[0], data[1]];
        var rightData = [data[2], data[3]];
        var upData = [data[4], data[5]];
        var downData = [data[6], data[7]];

        // Colors
        // pre-/post-med for voice, stand, tap, and walk activities:
        var colors = d3.scale.ordinal()
          .domain([1,2,3,4,5,6,7,8])
          .range(["#EEBE32", "#9F5B0D", "#B0A9B7", "#6F6975", "#EB7D65", "#C02504", "#20AED8", "#2C1EA2"]);
        var leftColors = [colors[0], colors[1]];
        var rightColors = [colors[2], colors[3]];
        var upColors = [colors[4], colors[5]];
        var downColors = [colors[6], colors[7]];

        // Set up variables:
        var half_cell_width = d3CalendarGlobals.cellWidth / 2;
        var outerRadius = half_cell_width;
        var innerRadius = 20;




        var pie = d3.layout.histogram();
        var glyph = d3.svg.arc().innerRadius(innerRadius).outerRadius(outerRadius);

        // Index and group the pie charts and slices so that they can be rendered in correct cells.
        // We call D3's 'pie' function of each of the data elements.
        var indexedData = [];
        for (i = 0; i < data.length; i++) {
            var pieSlices = pie(data[i]);
            // This loop stores an index (j) for each of the slices of a given pie chart.
            // Two different charts on different days will have the the same set of numbers for slices
            // (eg: 0,1,2). This will help us pick the same colors for the slices for independent charts.
            // Otherwise, the colors of the slices will be different each day.
            for (j = 0; j < number_of_values; j++) {
                indexedData.push([pieSlices[j], i, j]);
            }
        }

        var cellPositions = d3CalendarGlobals.gridCellPositions;

        d3CalendarGlobals.chartsGroup
                .selectAll("g.glyph")
                .remove();

        var glyphs = d3CalendarGlobals.chartsGroup.selectAll("g.glyph")
                      // Use the indexed data so that each pie chart can be drawn in a different cell:
//                      .data(indexedData)
                      .data(indexedData)
                      .enter()
                      .append("g")
                      .attr("class", "glyph")
                      // Use the index here to translate the glyph and render it
                      // in the appropriate cell. Normally, the glyph would be squashed up
                      // against the top left of the cell, obscuring the text that shows the day
                      // of the month. We use the gridXTranslation and gridYTranslation and multiply it
                      // by a factor to move it to the center of the cell. There is probably
                      // a better way of doing this, though.
                      .attr("transform", function (d) {
                          var currentDataIndex = d[1];
                          return "translate(" +  (half_cell_width + d3CalendarGlobals.gridXTranslation * 1 + cellPositions[currentDataIndex][0]) + ", " +  (half_cell_width + d3CalendarGlobals.gridYTranslation * 1 + cellPositions[currentDataIndex][1]) + ")";
                      });

        glyphs.append("path")
            // The color is generated using the second index.
            // Each slice of the pie is given a fixed number.
            // This applies to all charts (see the indexing loop above).
            // This way, by using the index we can generate the same colors
            // for each of the slices for different charts on different days.
            .attr("fill", function (d, i) {
//                return colors(i);
                return colors(d[2]);
            })
            // Standard functions for drawing a pie charts in D3:
            .attr("d", function (d, i) {
                return glyph(d[0]);
            });


/*
        var pie = d3.layout.histogram();
//        var pie = d3.layout.pie();
//        var pie = radial_bars();
        var glyph = d3.svg.arc().innerRadius(innerRadius).outerRadius(outerRadius);


        // Index and group the pie charts and slices so that they can be rendered in correct cells.
        // We call D3's 'pie' function of each of the data elements.
        var indexedData = [];
        for (i = 0; i < data.length; i++) {
            var pieSlices = pie(data[i]);
            // This loop stores an index (j) for each of the slices of a given pie chart.
            // Two different charts on different days will have the the same set of numbers for slices
            // (eg: 0,1,2). This will help us pick the same colors for the slices for independent charts.
            // Otherwise, the colors of the slices will be different each day.
            for (j = 0; j < pieSlices.length; j++) {
                indexedData.push([pieSlices[j], i, j]);
            }
        }

        var cellPositions = d3CalendarGlobals.gridCellPositions;

        d3CalendarGlobals.chartsGroup
                .selectAll("g.glyph")
                .remove();

        var glyphs = d3CalendarGlobals.chartsGroup.selectAll("g.glyph")
                      // Use the indexed data so that each pie chart can be drawn in a different cell:
                      .data(indexedData)
                      .enter()
                      .append("g")
                      .attr("class", "glyph")
                      // Use the index here to translate the glyph and render it
                      // in the appropriate cell. Normally, the glyph would be squashed up
                      // against the top left of the cell, obscuring the text that shows the day
                      // of the month. We use the gridXTranslation and gridYTranslation and multiply it
                      // by a factor to move it to the center of the cell. There is probably
                      // a better way of doing this, though.
                      .attr("transform", function (d) {
                          var currentDataIndex = d[1];
                          return "translate(" +  (half_cell_width + d3CalendarGlobals.gridXTranslation * 1 + cellPositions[currentDataIndex][0]) + ", " +  (half_cell_width + d3CalendarGlobals.gridYTranslation * 1 + cellPositions[currentDataIndex][1]) + ")";
                      });
*/
/*
        glyphs.append("path")
            // The color is generated using the second index.
            // Each slice of the pie is given a fixed number.
            // This applies to all charts (see the indexing loop above).
            // This way, by using the index we can generate the same colors
            // for each of the slices for different charts on different days.
            .attr("fill", function (d, i) {
//                return colors(i);
                return colors(d[2]);
            })
            // Standard functions for drawing a pie charts in D3:
            .attr("d", function (d, i) {
                return glyph(d[0]);
            });
*/

        //--------------------------------------------------------------------
        // Radial barchart function
        //--------------------------------------------------------------------
        function radial_bars() { 

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
        };



    //------------------------------------------------------------------------
    // Alternative (debugging): PIE CHARTS
    //------------------------------------------------------------------------
    } else {

        // Get data for a month:
        var number_of_values = 8
        var max_number = 100
        var data = getDataForMonth(number_of_values, max_number);

        // Set up variables required to draw a pie chart:
        var outerRadius = d3CalendarGlobals.cellWidth / 2;
        var innerRadius = 20;
        var pie = d3.layout.pie();
        var color = d3.scale.category10();
        var arc = d3.svg.arc().innerRadius(innerRadius).outerRadius(outerRadius);

        // Index and group the pie charts and slices so that they can be rendered in correct cells.
        // We call D3's 'pie' function of each of the data elements.
        var indexedPieData = [];
        for (i = 0; i < data.length; i++) {
            var pieSlices = pie(data[i]);
            // This loop stores an index (j) for each of the slices of a given pie chart.
            // Two different charts on different days will have the the same set of numbers for slices
            // (eg: 0,1,2). This will help us pick the same colors for the slices for independent charts.
            // Otherwise, the colors of the slices will be different each day.
            for (j = 0; j < pieSlices.length; j++) {
                indexedPieData.push([pieSlices[j], i, j]);
            }
        }

        var cellPositions = d3CalendarGlobals.gridCellPositions;

        d3CalendarGlobals.chartsGroup
                .selectAll("g.arc")
                .remove();

        var arcs = d3CalendarGlobals.chartsGroup.selectAll("g.arc")
                      // Use the indexed data so that each pie chart can be drawn in a different cell:
                      .data(indexedPieData)
                      .enter()
                      .append("g")
                      .attr("class", "arc")
                      // Use the index here to translate the pie chart and render it
                      // in the appropriate cell. Normally, the chart would be squashed up
                      // against the top left of the cell, obscuring the text that shows the day
                      // of the month. We use the gridXTranslation and gridYTranslation and multiply it
                      // by a factor to move it to the center of the cell. There is probably
                      // a better way of doing this, though.
                      .attr("transform", function (d) {
                          var currentDataIndex = d[1];
                          return "translate(" +  (outerRadius + d3CalendarGlobals.gridXTranslation * 1 + cellPositions[currentDataIndex][0]) + ", " +  (outerRadius + d3CalendarGlobals.gridYTranslation * 1 + cellPositions[currentDataIndex][1]) + ")";
                      });
        arcs.append("path")
            // The color is generated using the second index.
            // Each slice of the pie is given a fixed number.
            // This applies to all charts (see the indexing loop above).
            // By using the index we can generate the same colors
            // for each of the slices for different charts on different days.
            .attr("fill", function (d, i) {
                return color(d[2]);
            })
            // Standard functions for drawing pie charts in D3:
            .attr("d", function (d, i) {
                return arc(d[0]);
            });
        arcs.append("text")
            .attr("transform", function (d,i) {
                return "translate(" + arc.centroid(d[0]) + ")";
            })
        .attr("text-anchor", "middle")
        .text(function(d,i) {
            return d[0].value;
            });
    }
}



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
// CALENDAR
//----------------------------------------------------------------------------
// Store some global data that will be shared between different functions:
var d3CalendarGlobals = function() {
    var calendarWidth = 1080, 
    calendarHeight = 800,
    gridXTranslation = 100,
    gridYTranslation = 80,
    style_header_top = 40,
    cellColorForCurrentMonth = '#B2B2B2',
    cellColorForPreviousMonth = '#FFFFFF',
    counter = 0, // Keep track of the number of back/forward button presses and calculate the month.
    currentMonth = new Date().getMonth(),
    monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    datesGroup;
    function publicCalendarWidth() { return calendarWidth; }
    function publicCalendarHeight() { return calendarHeight; }
    function publicGridXTranslation() { return gridXTranslation; }
    function publicGridYTranslation() { return gridYTranslation; }
    function publicGridWidth() { return calendarWidth - gridXTranslation; }
    function publicGridHeight() { return calendarHeight - gridYTranslation - style_header_top + 20; }
    function publicCellWidth() { return publicGridWidth() / 7; }
    function publicCellHeight() { return publicGridHeight() / 5; }
    function publicGetDatesGroup() {
        return datesGroup;
    }
    function publicSetDatesGroup(value) {
        datesGroup = value;
    }
    function publicIncrementCounter() { counter = counter + 1; }
    function publicDecrementCounter() { counter = counter - 1; }

    // Display month based on the counter:
    function publicMonthToDisplay() {
        var dateToDisplay = new Date();
        dateToDisplay.setMonth(currentMonth + counter);
        return dateToDisplay.getMonth();
    }
    function publicMonthToDisplayAsText() { return monthNames[publicMonthToDisplay()]; }

    // Display year based on the counter:
    function publicYearToDisplay() {
        var dateToDisplay = new Date();
        dateToDisplay.setMonth(currentMonth + counter);
        return dateToDisplay.getFullYear();
    }

    // Store the top left positions of a 7 by 5 grid. 
    // These positions will be our reference points for drawing various objects
    // such as the rectangular grids, the text indicating the date, etc.
    function publicGridCellPositions() {
        var cellPositions = [];
        for (y = 0; y < 5; y++) {
            for (x = 0; x < 7; x++) {
                cellPositions.push([x * publicCellWidth(), y * publicCellHeight()]);
            }
        }
        return cellPositions;
    }

    // Generate all the days of the month. Since we have a 7 by 5 grid,
    // we need to get some of the days from the previous and the next month.
    // This way our grid will have all its cells filled, with a different color
    // for the days from the previous or next month.
    function publicDaysInMonth() {
        var daysArray = [];
        var firstDayOfTheWeek = new Date(publicYearToDisplay(), publicMonthToDisplay(), 1).getDay();
        var daysInPreviousMonth = new Date(publicYearToDisplay(), publicMonthToDisplay(), 0).getDate();
        // If the first week of the current month is a Wednesday, then we need to get 3 days 
        // from the end of the previous month, and do it properly, whether the last month
        // had 31, 30, 29, or 28 days.
        for (i = 1; i <= firstDayOfTheWeek; i++) {
            daysArray.push([daysInPreviousMonth - firstDayOfTheWeek + i, cellColorForCurrentMonth]);
        }
        // These are all the days in the current month.
        var daysInMonth = new Date(publicYearToDisplay(), publicMonthToDisplay() + 1, 0).getDate();
        for (i = 1; i <= daysInMonth; i++) {
            daysArray.push([i, cellColorForPreviousMonth]);
        }
        // Depending on how many days we have so far (from previous and current month), we will need
        // to get some days from next month. We can do this easily, since all months start on the 1st.
        var daysRequiredFromNextMonth = 35 - daysArray.length;
        for (i = 1; i <= daysRequiredFromNextMonth; i++) {
            daysArray.push([i,cellColorForCurrentMonth]);
        }
        return daysArray.slice(0,35);
    }

    return {
        calendarWidth: publicCalendarWidth(),
        calendarHeight: publicCalendarHeight(),
        gridXTranslation :publicGridXTranslation(),
        gridYTranslation :publicGridYTranslation(),
        gridWidth :publicGridWidth(),
        gridHeight :publicGridHeight(),
        cellWidth :publicCellWidth(),
        cellHeight :publicCellHeight(),
        getDatesGroup : publicGetDatesGroup,
        setDatesGroup: publicSetDatesGroup,
        incrementCounter : publicIncrementCounter,
        decrementCounter : publicDecrementCounter,
        monthToDisplay : publicMonthToDisplay(),
        monthToDisplayAsText : publicMonthToDisplayAsText,
        yearToDisplay: publicYearToDisplay,
        gridCellPositions: publicGridCellPositions(),
        daysInMonth : publicDaysInMonth
    }
}();

// Render calendar and days of the month:
$(document).ready( function (){
                    renderCalendarGrid();
                    renderDaysOfMonth();
                    $('#back').click(displayPreviousMonth);
                    $('#forward').click(displayNextMonth);
                    }
                    );

// Keep track of "back" and "forward" presses in this counter:
function displayPreviousMonth() {
    d3CalendarGlobals.decrementCounter();
    renderDaysOfMonth();
}
function displayNextMonth(){
    d3CalendarGlobals.incrementCounter();
    renderDaysOfMonth();
}

// Render the days of the month in the grid:
function renderDaysOfMonth(month, year) {
    $('#currentMonth').text(d3CalendarGlobals.monthToDisplayAsText() + ' ' + d3CalendarGlobals.yearToDisplay());
    // Days for the month are based on the number of backward/forward button presses:
    var daysInMonthToDisplay = d3CalendarGlobals.daysInMonth();
    var cellPositions = d3CalendarGlobals.gridCellPositions;
    // All text elements representing the dates are grouped together
    // in the "datesGroup" element by the initalizing function below,
    // which also draws the rectangles of the grid.
    d3CalendarGlobals.datesGroup 
     .selectAll("text")
     .data(daysInMonthToDisplay)
     .attr("x", function (d,i) { return cellPositions[i][0]; })
     .attr("y", function (d,i) { return cellPositions[i][1]; })
     .attr("dx", 5) // right padding
     .attr("dy", 19) // vertical alignment : middle
     .attr("transform", "translate(" + d3CalendarGlobals.gridXTranslation + "," + d3CalendarGlobals.gridYTranslation + ")")
     .text(function (d) { return d[0]; }); // Render text for the day of the week.
    // Rectangles for days not part of the current month are filled with a different color:
    d3CalendarGlobals.calendar
     .selectAll("rect")
     .data(daysInMonthToDisplay)
     .style("fill", function (d) { return d[1]; }); 
    drawGraphsForMonthlyData();
}

// This initializing function adds an svg element, draws rectangles to form the calendar grid,
// puts text in each cell for the date and does the initial rendering of the pie charts:
function renderCalendarGrid(month, year) {

    // Add the svg element:
    d3CalendarGlobals.calendar = d3.select("#chart")
                 .append("svg")
                 .attr("class", "calendar")
                 .attr("width", d3CalendarGlobals.calendarWidth )
                 .attr("height", d3CalendarGlobals.calendarHeight)
                 .append("g");

    // Cell positions are generated and stored globally because they are used by other functions
    // as a reference to render different things.
    var cellPositions = d3CalendarGlobals.gridCellPositions;

    // Draw rectangles at the appropriate positions, starting from the top left corner.
    // Since we want to leave some room for the header and buttons,
    // use the gridXTranslation and gridYTranslation variables.
    d3CalendarGlobals.calendar.selectAll("rect")
            .data(cellPositions)
            .enter()
            .append("rect")
            .attr("x", function (d) { return d[0]; })
            .attr("y", function (d) { return d[1]; })
            .attr("width", d3CalendarGlobals.cellWidth)
            .attr("height", d3CalendarGlobals.cellHeight)
            .style("stroke", "#555")
            .style("fill", "white") 
            .attr("transform", "translate(" + d3CalendarGlobals.gridXTranslation + "," + d3CalendarGlobals.gridYTranslation + ")");

    var daysOfTheWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    // Add the day of the week headers on top of the grid:
    d3CalendarGlobals.calendar.selectAll("headers")
         .data([0, 1, 2, 3, 4, 5, 6])
         .enter().append("text")
         .attr("x", function (d) { return cellPositions[d][0]; })
         .attr("y", function (d) { return cellPositions[d][1]; })
         .attr("dx", d3CalendarGlobals.gridXTranslation + 5) // right padding
         .attr("dy", d3CalendarGlobals.gridYTranslation - 10) // vertical alignment : middle
         .text(function (d) { return daysOfTheWeek[d] });

    // Initial rendering of the dates for the current month inside each of the cells in the grid.
    // Create a named group ("datesGroup"), and add our dates to this group.
    // This group is also stored globally. Later, when the the user presses the back/forward buttons
    // to navigate between the months, we clear and re-add the new text elements to this group:
    d3CalendarGlobals.datesGroup = d3CalendarGlobals.calendar.append("svg:g");
    var daysInMonthToDisplay = d3CalendarGlobals.daysInMonth();
    d3CalendarGlobals.datesGroup 
         .selectAll("daysText")
         .data(daysInMonthToDisplay)
         .enter()
         .append("text")
         .attr("x", function (d, i) { return cellPositions[i][0]; })
         .attr("y", function (d, i) { return cellPositions[i][1]; })
         .attr("dx", 20) // right padding
         .attr("dy", 20) // vertical alignment : middle
         .attr("transform", "translate(" + d3CalendarGlobals.gridXTranslation + "," + d3CalendarGlobals.gridYTranslation + ")")
         .text(function (d) { return d[0]; });

    // Create a new svg group to store the chart elements and store it globally.
    // Again, as the user navigates through the months by pressing the back/forward buttons,
    // we clear the chart elements from this group and add them again:
    d3CalendarGlobals.chartsGroup = d3CalendarGlobals.calendar.append("svg:g");
    // Call the function to draw the charts in the cells.
    // Call each time the user presses the forward or backward buttons:
    drawGraphsForMonthlyData();
}

