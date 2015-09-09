var bgs = [
	{
		cssUrl: "url('./kotori.png')",
		color: "#2DBC5F",
		text: "love live! school idol project"
	},
	{
		cssUrl: "url('./madoka.png')",
		color: "#E48397",
		text: "puella magi madoka magica"
	},
	{
		cssUrl: "url('./umaru.png')",
		color: "#FA885C",
		text: "himouto! umaru-chan"
	},
	{
		cssUrl: "url('./eureka.png')",
		color: "#A2D0C2",
		text: "eureka seven"
	},
	{
		cssUrl: "url('./shiro.png')",
		color: "#713FA4",
		text: "no game no life"
	},
	{
		cssUrl: "url('./rin.png')",
		color: "#B20B36",
		text: "fate/stay night"
	},
]

var popular = ["attack on titan", "fullmetal alchemist: brotherhood", "naruto", "one piece", "eureka seven", 
	"rokka -braves of the six flowers-", "love live! school idol project", "puella magi madoka magica", "dragon ball z"]
var providers = ["crunchyroll", "funimation", "hulu", "netflix", "viewster", "daisuki"]
var shows = []
var highlights = []
$(document).on('click', '.service:not(.na)', function(e){
	var show = $(this).parents('.result').children('.result-name').text()
	var service = $(this).attr('service')
	var searchTerm = $('.search-input').val()
	ga('send', 'event', service, show, searchTerm)
})

$(document).ready(function(){
	var showshound = {}
	$('.search-input').focus()
	$.getJSON("./bcmoe.json", function(data){
		shows = data
		setup()
	})
	function setup(){
		$('.search-icon').show()
		$('.search-clear').hide()
		var bg = bgs[Math.floor(Math.random()*bgs.length)]
		$('body').css("background-image", bg.cssUrl);
		$('h4').css("color", bg.color);
		$('.search-input').attr("placeholder", bg.text)
		showshound = new Bloodhound({
			datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
			queryTokenizer: Bloodhound.tokenizers.whitespace,
			local: shows
		});
		
		highlights = shows.filter(function(show){
			return (popular.indexOf(show.name.toLowerCase()) > -1)
		}).sort(function(a, b){
			if (a.name < b.name) return -1;
			if (a.name > b.name) return 1;
			return 0;
		})
		updateShowList(highlights);
	}
	
	
	function updateShowList(showList, message){
		$('.results-container').empty();
		if (message){
			$('.results-container').append("<div class='result message'>"+ message + "</div>");
		}
		if (showList.length == 0){
			$('.results-container').append("<div class='result message'>No Results</div>");
		} else {
			showList.forEach(function(show){
				var resultHtml = "<div class='result'><div class='result-name'>" + show.name + "</div>";
				var sites = Object.keys(show.sites);
				resultHtml += "<div class='services-container'>";
				
				if (show.sites.crunchyroll){
					resultHtml += "<a href='" + show.sites.crunchyroll + "' target='_blank'><div class='service service-crunchyroll' service='crunchyroll'></div></a>"
				} else {
					resultHtml += "<div class='service service-crunchyroll na'></div>"
				}
				
				if (show.sites.funimation){
					resultHtml += "<a href='" + show.sites.funimation + "' target='_blank'><div class='service service-funimation' service='funimation'></div></a>"
				} else {
					resultHtml += "<div class='service service-funimation na'></div>"
				}
				
				if (show.sites.hulu){
					resultHtml += "<a href='" + show.sites.hulu + "' target='_blank'><div class='service service-hulu' service='hulu'></div></a>"
				} else {
					resultHtml += "<div class='service service-hulu na'></div>"
				}
				
				if (show.sites.netflix){
					resultHtml += "<div class='service service-netflix' service='netflix'></div></a>"
				} else {
					resultHtml += "<div class='service service-netflix na'></div>"
				}
				if (show.sites.viewster){
					resultHtml += "<a href='" + show.sites.viewster + "' target='_blank'><div class='service service-viewster' service='viewster'></div></a>"
				} else {
					resultHtml += "<div class='service service-viewster na'></div>"
				}
				
				if (show.sites.daisuki){
					resultHtml += "<a href='" + show.sites.daisuki + "' target='_blank'><div class='service service-daisuki' service='daisuki'></div></a>"
				} else {
					resultHtml += "<div class='service service-daisuki na'></div>"
				}
				
				resultHtml += "</div></div>"
				$('.results-container').append(resultHtml);
			})
		}
		//console.log(showList);
	}
	$('.search-clear').on('click', function(){
		$('.search-input').val('');
		resultsUpdate();
	})
		
	$('.search-input').on('input', function(){
		resultsUpdate();
	})
	
	function resultsUpdate(){
		if ($('.search-input').val() === '') { 
			$('.search-icon').show()
			$('.search-clear').hide()
			updateShowList(highlights)
		} else if (providers.indexOf($('.search-input').val().toLowerCase()) > -1){ 
			$('.search-icon').hide()
			$('.search-clear').show()
			var providerIndex = providers.indexOf($('.search-input').val().toLowerCase());
			updateShowList(shows.filter(function(show){
				return providers[providerIndex] in show['sites']
			}))
		} else {
			$('.search-icon').hide()
			$('.search-clear').show()
			showshound.search($('.search-input').val(), updateShowList);
		}
	}
})