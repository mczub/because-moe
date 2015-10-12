var bgs = [
	{
		cssUrl: "url('./bg/kotori.png')",
		color: "#2DBC5F",
		text: "love live! school idol project"
	},
	{
		cssUrl: "url('./bg/madoka.png')",
		color: "#E48397",
		text: "puella magi madoka magica"
	},
	{
		cssUrl: "url('./bg/umaru.png')",
		color: "#FA885C",
		text: "himouto! umaru-chan"
	},
	{
		cssUrl: "url('./bg/eureka.png')",
		color: "#A2D0C2",
		text: "eureka seven"
	},
	{
		cssUrl: "url('./bg/shiro.png')",
		color: "#713FA4",
		text: "no game no life"
	},
	{
		cssUrl: "url('./bg/rin.png')",
		color: "#B20B36",
		text: "fate/stay night"
	},
]

var popular = ["attack on titan", "fullmetal alchemist: brotherhood", "naruto", "one piece", "eureka seven", 
	"rokka: braves of the six flowers", "love live! school idol project", "puella magi madoka magica", "dragon ball z"]
var providers = {
	'us': ["crunchyroll", "funimation", "hulu", "netflix", "viewster", "daisuki", "animenetwork"], 
	'ca': ["crunchyroll", "funimation", "netflix", "viewster", "daisuki", "animenetwork"], 
	'uk': ["crunchyroll", "netflix", "viewster", "daisuki", "animax"],
	'au': ["crunchyroll", "netflix", "viewster", "daisuki", "animelab", "hanabee"]
}
var jsons = {
	'us': './json/us',
	'ca': './json/ca',
	'uk': './json/uk',
	'au': './json/au'
}
var shows = []
var lastUpdated = {}
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
	$('.' + region).removeClass('no')
	console.log(region)
	$.getJSON(jsons[region], function(data){
		if (data.shows){
			shows = data.shows
			lastUpdated = moment.utc(data.lastUpdated)
		} else {
			shows = data
		}
		setup()
		if (query !== ""){
			$('.search-input').val(query);
			resultsUpdate();
		}
	})
	
	function setup(){
		$('.search-icon').show()
		$('.search-clear').hide()
		if (!$.isEmptyObject(lastUpdated)){
			$('.last-updated').text("Last Updated: " + lastUpdated.local().format("MMM DD HH:mm"))
		}
		var bg = bgs[Math.floor(Math.random()*bgs.length)]
		$('body').css("background-image", bg.cssUrl);
		$('h4').css("color", bg.color);
		$('.search-input').attr("placeholder", bg.text)
		showshound = new Bloodhound({
			datumTokenizer: function(show){
				return Bloodhound.tokenizers.whitespace(show.name + ' ' + (show.alt ? show.alt : ''))
			},
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
				var resultHtml = "<div class='result'><div class='result-name'>" + show.name;
				if (show.alt){
					resultHtml += "<div class='result-alt mobile-hide'>" + show.alt + "</div>"
				}
				var sites = Object.keys(show.sites);
				resultHtml += "</div><div class='services-container'>";
				providers[region].forEach(function(provider){
					if (show.sites[provider]){
						if (typeof show.sites[provider] === 'string' || show.sites[provider] instanceof String){
							resultHtml += "<a href='" + show.sites[provider] + "' target='_blank'><div class='service service-" + provider + "' service='" + provider + "'></div></a>"
						} else {
							resultHtml += "<div class='service service-" + provider + "' service='" + provider + "'></div>"
						}
						
					} else {
						resultHtml += "<div class='service service-" + provider + " na'></div>"
					}
				})
							
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
		} else if (providers[region].indexOf($('.search-input').val().toLowerCase()) > -1){ 
			$('.search-icon').hide()
			$('.search-clear').show()
			var providerIndex = providers[region].indexOf($('.search-input').val().toLowerCase());
			updateShowList(shows.filter(function(show){
				return providers[region][providerIndex] in show['sites']
			}))
		} else {
			$('.search-icon').hide()
			$('.search-clear').show()
			showshound.search($('.search-input').val(), updateShowList);
		}
	}
})