var getDescription = function (file, id) {
    $('#included-description').load(file + "#" + id);
};

var getGraphScript = function (scriptfile) {
    var script = document.createElement("script");

    script.type = "text/javascript";
    script.src = scriptfile;
    script.id = scriptfile;

    if($('#myscript').length == 0) {
         document.getElementById("included-description").appendChild(script);
    }
      document.getElementById( scriptfile).parentNode.removeChild(document.getElementById(scriptfile) );
};

//load view 1
getDescription("frontend/graph_descriptions.html ", "view-1-description");

//start tweet counter
countTweets();

// load graph scripts
getGraphScript("frontend/view1script.js");

//underline view Navigation
$('li.ex-bar-item').click(function (e) {
    e.preventDefault();
    $("span").removeClass("active");
    $("a").removeClass("hover-bar");
    $(this).find('span:first').addClass("active");
    $(this).find('a:first').addClass("hover-bar");

    //based on which view user clicked it loads corresponding script
    switch (this.getAttribute("id")) {
        case "view1":
            getDescription("frontend/graph_descriptions.html ", "view-1-description");
            getGraphScript("frontend/view1script.js");
            break;
        case "view2":
            getDescription("frontend/graph_descriptions.html ", "view-2-description");
            getGraphScript("frontend/view2script.js");
            break;
    }
});

function countTweets() {
  $.ajax({
      url: "/gettweetcount",
      success: function(data) {
        document.getElementById("tweet-counter").innerHTML = data;
      },
      complete: function() {
      // Schedule the next request when the current one's complete
        setTimeout(countTweets, 5000);
      }
  });
}