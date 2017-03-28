
$(function() {

    "use strict";

    function updateSalesRankChart (data, markers) {
        var tip = d3.tip()
            .attr('class', 'd3-tip')
            .offset([-10, 0])
            .html(function (d) {
                return d.date.toISOString().slice(0, 10) + " : <span style='color:red; margin-left: 5px;'>" +
                           d.salesrank +
                       "</span>";
            });

        var width = 900;
        var height = 333;
        var barPadding = 1;

        // Parse the date / time
        var	parseDate = d3.time.format("%Y-%m-%d").parse;

        var x = d3.scale.ordinal().rangeRoundBands([0, width], 0.05);
        var y = d3.scale.linear().range([height, 0]);

        var svg = d3.select("#avg-salesrank-by-day")
                    .append("svg")
                      .attr("width", width)
                      .attr("height", height);

        svg.call(tip);

        data.forEach(function(d) {
            d.date = parseDate(d.date);
            d.value = d.salesrank;
        });


        x.domain(data.map(function(d) { return d.date; }));
        y.domain([0, d3.max(data, function(d) { return d.value; })]);

        svg.selectAll(".bar")
            .data(data)
            .enter()
                .append("rect")
                    .attr("class", "bar")
                    .attr("x", function(d) { return x(d.date); })
                    .attr("width", x.rangeBand() - 1)
                    .attr("y", function(d) { return y(d.value); })
                    .attr("height", function(d) { return height - y(d.value); })
                    .on('mouseover', tip.show)
                    .on('mouseout', tip.hide);


        // Define the div for the tooltip
        var div = d3.select("body").append("div")
                    .attr("class", "tooltip")
                    .style("opacity", 0);

        markers.forEach(function(d) {
            d.date = parseDate(d.action_date);
            d.value = d.salesrank;
        });

        svg.selectAll('.marker')
            .data(markers)
            .enter()
                .append("line")
                .attr("x1", function(d) {
                    return x(d.date);
                })
                .attr("y1", 0)
                .attr("x2", function(d) { return x(d.date); })
                .attr("y2", height)
                .style("stroke-dasharray", ("3, 3"))  // <== This line here!!
                .style("stroke-width", 3)
                .style("stroke", "grey")
                .on("mouseover", function(d) {
                    div.transition()
                        .duration(100)
                        .style("opacity", 0.9);
                    div.html(d.date.toISOString().slice(0, 10) + ": <span style='color:red; margin-left: 5px;'>" +
                            d.description +
                            "</span>")
                        .style("left", (d3.event.pageX + 10) + "px")
                        .style("top", (d3.event.pageY - 30) + "px");
                    })
                .on("mouseout", function(d) {
                    div.transition()
                        .duration(500)
                        .style("opacity", 0);
                });
    }

    var numberOfValues = 100;

    $('#datetimepicker_from').datetimepicker();
    $('#datetimepicker_to').datetimepicker({
        useCurrent: false //Important! See issue #1075
    });

    function updateCharts (from_date, to_date) {

        var salesranks = [];
        var prices = [];

        var urlChunks = window.location.href.split('/');
        var sku = urlChunks[urlChunks.length - 2];

        var dataset_salesranks = null;
        var dataset_prices = null;

        // TODO: Use detail url
        var url = '/api/salesrankhistories-by-day/?sku=' + sku;
        if (from_date && to_date) {
            url += '&from_date=' + from_date + '&to_date=' + to_date;
        }

        $.getJSON( url, function (data) {
            $.each( data, function (i, obj) {
                salesranks.push({
                    'date': obj._time.slice(0,10),
                    'salesrank': obj.salesrank
                });
                prices.push({
                    'date': obj._time.slice(0,10),
                    'price': parseInt(obj.price)
                });
            });

            var markerUrl = '/api/productmarkers/?sku=' + sku;
            if (from_date && to_date) {
                url += '&from_date=' + from_date + '&to_date=' + to_date;
            }
            $.getJSON(markerUrl, function (markers) {

                dataset_salesranks = salesranks.slice(salesranks.length - numberOfValues, salesranks.length);
                dataset_prices = prices.slice(prices.length - numberOfValues, prices.length);

                // drawPriceChart(dataset_prices, "#avg-price-by-day");
                updateSalesRankChart(dataset_salesranks, markers);
                updatePriceChart(dataset_prices);

            })
            .fail(function() {
                console.log( "error marker" );
            });

        })
        .fail(function() {
            console.log( "error" );
        });

    }

    function updatePriceChart (data) {

        var width = 900;
        var height = 200;
        var barPadding = 1;

        var tip = d3.tip()
            .attr('class', 'd3-tip')
            .offset([-10, 0])
            .html(function (d) {
                return d.date.toISOString().slice(0, 10) + " : <span style='color:red; margin-left: 5px;'>" +
                    d.price +
                    "</span>";
            });

        // Parse the date / time
        var	parseDate = d3.time.format("%Y-%m-%d").parse;

        var x = d3.scale.ordinal().rangeRoundBands([0, width], 0.05);
        var y = d3.scale.linear().range([height, 0]);

        var svg = d3.select("#avg-price-by-day")
                    .append("svg")
                      .attr("width", width)
                      .attr("height", height);
        svg.call(tip);

        data.forEach(function(d) {
            d.date = parseDate(d.date);
            d.value = d.price;
        });

        x.domain(data.map(function(d) { return d.date; }));
        y.domain([0, d3.max(data, function(d) { return d.value; })]);

        svg.selectAll(".bar")
            .data(data)
            .enter()
                .append("rect")
                    .attr("class", "bar")
                    .attr("x", function(d) { return x(d.date); })
                    .attr("width", x.rangeBand() - 1)
                    .attr("y", function(d) { return y(d.value); })
                    .attr("height", function(d) { return height - y(d.value); })
                .on('mouseover', tip.show)
                .on('mouseout', tip.hide);
    }


    /**************************************************************************
    *
    *  actionListeners
    *
    ***************************************************************************/
    $("#datetimepicker_from").on("dp.change", function (e) {
        $('#datetimepicker_to').data("DateTimePicker").minDate(e.date);
    });
    $("#datetimepicker_to").on("dp.change", function (e) {
        $('#datetimepicker_from').data("DateTimePicker").maxDate(e.date);
    });

    $("#product-submit-datepicker").click(function () {
        var from_date = $('#datetimepicker_from').data().date.slice(0,10).replace(/\//g, '-');
        var to_date = $('#datetimepicker_to').data().date.slice(0,10).replace(/\//g, '-');
        updateCharts(from_date, to_date);
    });

    /**************************************************************************
    *
    *  init ()
    *
    ***************************************************************************/
    updateCharts();

});
