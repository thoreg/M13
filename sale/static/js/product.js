$(function() {

    var numberOfValues = 100;
    var salesranks = [];
    var prices = [];
    var urlChunks = window.location.href.split('/');
    var sku = urlChunks[urlChunks.length - 2];

    $.getJSON("/api/salesrankhistories-by-day/?sku=" + sku, function (data) {

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

        var dataset_salesranks = salesranks.slice(0, numberOfValues);
        var dataset_prices = prices.slice(0, numberOfValues);

        drawSalesRankChart(dataset_salesranks, "#avg-salesrank-by-day");
        drawPriceChart(dataset_prices, "#avg-price-by-day");

    });

    function drawSalesRankChart (dataset, cssId) {

        var tip = d3.tip()
            .attr('class', 'd3-tip')
            .offset([-10, 0])
            .html(function (d) {
                return d.date + " : <span style='color:red; margin-left: 5px;'>" +
                           d.salesrank +
                       "</span>";
            })

        var width = 800;
        var height = 600;
        var barPadding = 1;  // <-- New!

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
                    return height - (d.salesrank * 0.004);
                })
                .attr("width", width / dataset.length - barPadding)
                .attr("height", function (d) {
                    return height * d.salesrank;
                })
                .on('mouseover', tip.show)
                .on('mouseout', tip.hide);

    };

    function drawPriceChart (dataset, cssId) {

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
                    return height - (d.price * 4);
                })
                .attr("width", width / dataset.length - barPadding)
                .attr("height", function (d) {
                    return height * d.price;
                })
                .on('mouseover', tip.show)
                .on('mouseout', tip.hide);
    }

});
