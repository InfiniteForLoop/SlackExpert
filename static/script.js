$(document).ready(function() {
  $("#random").click(function() {
    window.open("https://wikipedia.org/wiki/Special:Random");    
  });
  
  $("#searchInput").keyup(function(event){
    if(event.keyCode == 13){
        $("#search").click();
    }
  });
  
  $("#search").click(function() {
    if ($("#searchInput").val() == "") {
      alert("I SEE YOU TRYING TO BREAK MY CODE! TRY AGAIN... JERK");
    } else {
      $("#title").animate({marginTop: "3%"}, "2000ms");
      
      var wikiSearch = "https://wikipedia.org/w/api.php?action=query&prop=revisions&format=json&list=search&srsearch="
      var searchee = $("#searchInput").val().replace(" ", "+");
      var ender = "&callback=?"
      var html = "";

      $.getJSON(wikiSearch + searchee + ender, function(json) { 
        json = json.query.search.forEach(function(val) {
          html += "<a href='https://wikipedia.org/wiki/" + val.title.replace(" ", "_") + "'><div class='searchResult'><h3 class='title'>" + val.title + "</h3><p>" + val.snippet + "... <i>(click to see more)</i></p></div></a>";
        });
        $("#searchResult").hide().html(html);
        $("#searchResult").fadeIn(2000, "swing");
      });
    };
  });
});