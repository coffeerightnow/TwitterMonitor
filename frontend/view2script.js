//contains json object for display
var dataContainer;
var width = document.getElementById("slider-container-2").offsetWidth;
var height =500;
var margin = {
    top: 50,
    right:20,
    bottom:50,
    left:50
};
var parseTime = d3.timeParse("%Y-%m-%d");
var path = "http://blockchainmediamonitor.enterpriselab.ch";

//HTML Slider
var slider2 = document.getElementById("slider-2");

//add listeners
slider2.oninput = function () {
    document.getElementById("current-slider-2-value").innerHTML = slider2.value;
    document.getElementById("view-title-2").innerHTML = "TOP " + slider2.value + " #HASHTAGS LINKED TO #BLOCKCHAIN";
};

slider2.onmouseup = function () {
    //remove whole svg
    getTimelineTweets(slider2.value);
};

window.addEventListener("resize", function(){
    width = document.getElementById("slider-container-2").offsetWidth;
    getTimelineTweets(slider2.value);
}, true);

// Get the data
getTimelineTweets(slider2.value);

function InitChart(p_data) {
    var color = d3.scaleOrdinal(d3.schemeCategory20);

    d3.selectAll("#svg-container-2 > svg").remove();
    dataContainer = p_data;

    dataContainer.forEach(function(d){
        d.daily_total_tweets = parseInt(d.daily_total_tweets);
        d.date =  parseTime(d.date);
    });

    var dataGroup = d3.nest()
        .key(function(d) {return d.name;})
        .entries(dataContainer);

    //label distance...
    var lSpace =  (width) / dataGroup.length;

    var xScale = d3.scaleLinear();
    xScale.range([margin.left, width - margin.right]);
    xScale.domain([d3.min(dataContainer, function(d) {return d.date;
    }), d3.max(dataContainer, function(d) {
        return d.date;
    })]);

    var yScale = d3.scaleLinear();
    yScale.range([height - margin.top, margin.bottom]);
    yScale.domain([d3.min(dataContainer, function(d) {
        return d.daily_total_tweets;
    }), d3.max(dataContainer, function(d) {
        return d.daily_total_tweets;
    })]);

    var lineGen = d3.line()
    .x(function(d) {
        return xScale(d.date);
    })
    .y(function(d) {
        return yScale(d.daily_total_tweets);
    });

    var xAxis = d3.axisBottom()
        .scale(xScale)
        .tickFormat(d3.timeFormat("%d-%m-%y"));

    var yAxis = d3.axisLeft()
        .scale(yScale);

    var svg = d3.select("#svg-container-2")
        .append("svg")
        .attr("width", "100%")
        .attr("height", height);

    dataGroup.forEach(function(d,i) {
        svg.append("path")
        .attr("d", lineGen(d.values))
        .attr("stroke", function(d,j) {
                return color(i);
        })
        .attr("stroke-width", 3.5)
        .attr("id", "line_"+d.key)
        .attr("fill", "none")
        .append("svg:title")
        .text(function() { return "#"+d.key; });

        svg.append("text")
            .attr("class","legend")
            .attr("x", (lSpace/2)+i*lSpace)
            .attr("y", height)
            .on("click",function(){
                var active   = d.active ? false : true;
                var opacity = active ? 0 : 1;
                d3.select("#line_" + d.key).style("opacity", opacity);
                d.active = active;
            })
            .style("fill",color(i))
            .text("#"+d.key);
    });

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + (height - margin.bottom) + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + margin.left + ",0)")
        .call(yAxis);
}

function getTimelineTweets(quantity) {
    $.ajax({
        url: path + "/timeline/" + quantity,
        type: "GET",
        dataType: "json",
        async: false,
        success:
            function (response) {
                dataContainer = response;
                InitChart(dataContainer);
            },
        error: function (error) {
            console.log(error);
        }
    });
}