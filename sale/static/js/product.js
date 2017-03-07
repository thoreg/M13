$(function() {

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

            var dataset_salesranks = salesranks.slice(salesranks.length - 100, salesranks.length);
            var dataset_prices = prices.slice(prices.length - 100, prices.length);

            drawSalesRankChart(dataset_salesranks, "#avg-salesrank-by-day");
            drawPriceChart(dataset_prices, "#avg-price-by-day");

        });

    };

    function drawSalesRankChart (dataset, cssId) {

        $("#avg-salesrank-by-day").html('');

        var tip = d3.tip()
            .attr('class', 'd3-tip')
            .offset([-10, 0])
            .html(function (d) {
                return d.date + " : <span style='color:red; margin-left: 5px;'>" +
                           d.salesrank +
                       "</span>";
            })

        var width = 800;
        var height = 333;
        var barPadding = 1;

        var yScale = d3.scale.linear()
                        .domain([0, d3.max(dataset, function(d) {
                            return d.salesrank;
                        })])
                        .range([0, height]);

        var svg = d3.select(cssId)
                    .append("svg")
                    .attr("width", width)
                    .attr("height", height);

        svg.call(tip);

        svg.selectAll(".bar")
            .data(dataset)
            .enter()
                .append("rect")
                .attr("class", "bar")
                .attr("x", function (d, i) {
                    return i * (width / dataset.length);
                })
                .attr("y", function (d) {
                    return height - yScale(d.salesrank);
                })
                .attr("width", width / dataset.length - barPadding)
                .attr("height", function (d) {
                    return height * yScale(d.salesrank);
                })
                .on('mouseover', tip.show)
                .on('mouseout', tip.hide);

    };

    function drawPriceChart (dataset, cssId) {

        $('#avg-price-by-day').html('');

        var tip = d3.tip()
            .attr('class', 'd3-tip')
            .offset([-10, 0])
            .html(function (d) {
                return d.date + " : <span style='color:red; margin-left: 5px;'>" +
                           d.price +
                       "</span>";
            })

        var width = 800;
        var height = 200;
        var barPadding = 1;

        var yScale = d3.scale.linear()
                        .domain([0, d3.max(dataset, function(d) {
                            return d.price;
                        })])
                        .range([0, height]);

        var svg = d3.select(cssId)
                    .append("svg")
                    .attr("width", width)
                    .attr("height", height);

        svg.call(tip);

        svg.selectAll(".bar")
            .data(dataset)
            .enter()
                .append("rect")
                .attr("class", "bar")
                .attr("x", function (d, i) {
                    return i * (width / dataset.length);
                })
                .attr("y", function (d) {
                    return height - yScale(d.price);
                })
                .attr("width", width / dataset.length - barPadding)
                .attr("height", function (d) {
                    return height * yScale(d.price);
                })
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
