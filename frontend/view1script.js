var w = document.getElementById('svg-container-1').offsetWidth; //dynamic width
var h = 800;
var path= "";

var nodeColor = "rgb(231, 54, 54)";
var nodeColorOnHover = "rgb(255, 80,80)";
var leafColorOnHover = "rgb(255, 210, 48)";
var leafColor = "rgb(255, 179, 49)";
var minNodeSize = 3;
var maxNodeSize = 90;
//initial values only!
var edgeDistance = 145;
var forceStrength = -85;
//Original data, contains the raw data from the backend response.
var dataSet;
var termList;
//holds the items for the searchbar dropdown list
var datalist = document.getElementById("json-datalist");
var input = document.getElementById("searchbar");

//defines the zoom levels
var zoom = d3.zoom()
	.scaleExtent([0.1, 10])
	.on("zoom", zoomed);

var svg = d3.select("#svg-container-1")
    .append("svg")
    .attr("width", "100%")
    .attr("height", h)
    .call(zoom)
    .append("g");

var slider = document.getElementById("slider-1");

function visualizeData(){
    var maxi = getMax(dataSet.nodes, "total_count");
    //define scaling function for circle area
    var aScale = d3.scaleSqrt()
        .domain([0, maxi.total_count])
        .range([minNodeSize, maxNodeSize]);

    //define behaviour of forces
    var myForce = d3.forceSimulation(dataSet.nodes)
        // defines attraction of nodes - the more the attracted
        //Note: it decreases the more nodes are in the graph so the expanded nodes don't repel each other too quickly
        .force("charge", d3.forceManyBody().strength(forceStrength+parseInt(slider.value)))
        //defines length of nodes
        .force("link", d3.forceLink(dataSet.edges).distance(edgeDistance))
        //sets center of svg and also start position of node center
        .force("center", d3.forceCenter().x(w / 2).y(h / 2.3))
        .on("tick", ticked);

    //Create a line for each edge
    var myEdges = svg.selectAll("line")
        .data(dataSet.edges)
        .enter()
        .append("line");

    //Create a circle for each node
    var myNodes = svg.selectAll(".node")
        .data(dataSet.nodes)
        .enter()
        .append("g").attr("class", "node")

        //add new data of expanded node to dataset
        .on("click", function (d) {
            // ignore drag
            if (d3.event.defaultPrevented) return;
                if (d.leaf == "false") {
                    getExpandedTree(slider.value, d.hashtag);
                    d3.selectAll("svg > g > *").remove();
                    visualizeData();
                }
            }
        )
        .on("mouseover", function () {
            d3.select(this).raise();
            d3.select(this).select("circle")
                .transition()
                .style("fill", function (d) {
                    if (d.leaf == "true") {
                        return leafColorOnHover;
                    }
                    return nodeColorOnHover;
                });
        })
        .on("mouseout", function () {
            d3.select(this).order();
            d3.select(this).select("circle")
                .transition()
                .style("fill", function (d) {
                    if (d.leaf == "true") {
                        return leafColor;
                    }
                    return nodeColor;
                });
        })
        .call(d3.drag()
            .on("start", dragStarted)
            .on("drag", dragging)
            .on("end", dragEnded));
    //set size of circle
    myNodes.append("circle").attr("r", function (d) {
        //use circle area - not radius
        return aScale(d.total_count);
    })
        .style("fill", function (d) {
            if (d.leaf == "true") {
                return leafColor;
            }
            return nodeColor;
        });

    //Add a simple tooltip
    myNodes.append("title")
        .text(function (d) {
            return d.total_count + " Tweets";
        });

    myEdges.append("title").text(function (d) {
        return d.occurance + " Tweets";
    });

    myNodes.append("text")
        .attr("dx", 12)
        .attr("dy", ".35em")
        .text(function (d) {
            return "#" + d.hashtag;
        });
    //Every time the simulation "ticks", this will be called
    function ticked() {
        myEdges.attr("x1", function (d) {
            return d.source.x;
        })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            });

        myNodes.attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        });
    }

    //#Define drag event functions
    function dragStarted(d) {
        if (!d3.event.active) myForce.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragging(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function dragEnded(d) {
        if (!d3.event.active) myForce.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    //extract max values
    function getMax(arr, prop) {
        var max;
        for (var i = 0; i < arr.length; i++) {
            if (!max || parseInt(arr[i][prop]) > parseInt(max[prop]))
                max = arr[i];
        }
        return max;
    }

    //extract min values
    function getMin(arr, prop) {
        var min;
        for (var i = 0; i < arr.length; i++) {
            if (!min || parseInt(arr[i][prop]) < parseInt(min[prop]))
                min = arr[i];
        }
        return min;
    }
}

function refreshGraph() {
    d3.selectAll("svg > g > *").remove();
    getDataFromDataBase(slider.value);
    visualizeData();
}

function zoomed() {
  svg.attr("transform", d3.event.transform);
}

function getDataFromDataBase(maxCount) {
    $.ajax({
        url: path+"/hashtag/" + maxCount,
        type: "GET",
        dataType: "json",
        async: false,
        success:
            function (response) {
                edgeDistance = 145;
                forceStrength = -85;
                dataSet = response;
            },
        error: function (error) {
            console.log(error);
        }
    })
    ;
}

function getExpandedTree(maxCount, hashtag) {
    $.ajax({
        url: path+"/expanded_tree?quantity=" + maxCount + "&hashtag=" + hashtag,
        type: "GET",
        dataType: "json",
        async: false,
        success:
            function (response) {
                dataSet = response;
            },
        error: function (error) {
            console.log(error);
        }
    })
    ;
}

function getTermList(quantity) {
    $.ajax({
        url: path+"/termlist/" + quantity,
        type: "GET",
        dataType: "json",
        async: false,
        success:
            function (response) {
                termList = response;
            },
        error: function (error) {
            console.log(error);
        }
    })
    ;
}

function getNodeByHashtag(quantity, hashtag) {
    $.ajax({
        url: path+"/hashtagsearch?quantity=" + quantity + "&hashtag=" + hashtag,
        type: "GET",
        dataType: "json",
        async: false,
        success:
            function (response) {
                d3.selectAll("svg > g > *").remove();
                dataSet = null;
                dataSet = response;

                //the bubbles are usually very big in this case, since the center is not the huge blockcain hashtag
                edgeDistance = 185;
                forceStrength = -250;
                visualizeData();
            },
        error: function (error) {
            console.log(error);
        }
    })
    ;
}

//fills the search bar with options
function populateDatalistOptions(){
    //sort termlist by alphabet
    termList = termList.sort();

    for(var i in termList)
    {
       //create a new <option> element
        var option = document.createElement("option");
        //Set the value using the item in the JSON array.
        option.value = termList[i];
        //add the <option> element to the <datalist>
        datalist.appendChild(option);
    }
    //update the placeholder text
    input.placeholder = "Choose a hashtag";
}

//fetches & displays data based on searchbar
function getNodesByInput(){
    //validate user input
    var $textInput = $("#searchbar");
    var val=$("#searchbar").val();
    var obj=$("#json-datalist").find("option[value='"+val+"']");

    if(obj !==null && obj.length>0){
        //removes error message if already existed
        document.getElementById("error-message-1").innerHTML = " ";
        $textInput.removeClass("placeholderred");

        //fetches the data

        getNodeByHashtag(slider.value,document.getElementById("searchbar").value );
        input.placeholder = "Choose a hashtag";
    } else {
         //update the placeholder text
         $textInput.addClass("placeholderred");
         document.getElementById("error-message-1").innerHTML = "No data available on this search term.";
    }
    if($textInput.val().toString().substring(0,1)=="#"){
         $textInput.addClass("placeholderred");
         document.getElementById("error-message-12").innerHTML = "Term must not start with #.";
    }
}

function init(){
    slider.oninput = function () {
        document.getElementById("current-slider-1-value").innerHTML =  slider.value;
        document.getElementById("view-1-title").innerHTML = "TOP " + slider.value + " #HASHTAGS LINKED TO #BLOCKCHAIN";
    };

    slider.onmouseup = function () {
        refreshGraph();
    };

    getDataFromDataBase(10);
    d3.selectAll("svg > g > *").remove();
    $("#flex-container").append("<p id='error-message-1'></p>");
    window.addEventListener("resize", function(){
        w = document.getElementById("svg-container-1").offsetWidth;
    }, true);

    visualizeData();
    getTermList(1250);
    populateDatalistOptions();
}

init();


