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

var popular = ["attack on titan", "fullmetal alchemist: brotherhood", "monthly girls' nozaki-kun", "hunter x hunter", "eureka seven", 
	"one punch man", "love live! school idol project", "dragon ball z"]
var popImg = {
	"Attack on Titan": "./shows/attack-on-titan.png",
	"Dragon Ball Z" : "./shows/dragon-ball-z.png",
	"One Punch Man" : "./shows/one-punch-man.png",
	"Eureka Seven" : "./shows/eureka-seven.png",
	"Fullmetal Alchemist: Brotherhood": "./shows/full-metal-alchemist-brotherhood.png",
	"Love Live! School Idol Project": "./shows/love-live.png",
	"Monthly Girls' Nozaki-kun": "./shows/nozaki.png",
	"Hunter x Hunter" : "./shows/hunter-x-hunter.png"
}
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
	'au': './json/au',
	'current': './current.json'
}
var shows = []
var currents = {}
var lastUpdated = {}
var highlights = []
$(document).on('click', '.service:not(.na)', function(e){
	var show = $(this).parents('.result').children('.result-name').text()
	var service = $(this).attr('service')
	var searchTerm = $('.search-input').val()
	ga('send', 'event', service, show, searchTerm)
})

$(document).on('change', '.region-selector', function(e){
	window.location = "/" + $('.region-selector').val().toLowerCase();
	$('.region-selector').val('');
})

$(document).ready(function(){
	var showshound = {}
	$('.search-input').focus()
	$('.region-selector').css('background-image', 'url("./flags/' + region + '.svg")');
	$('.region-selector').val(region.toUpperCase())
	console.log(region)
	$.getJSON(jsons[region], function(data){
		if (data.shows){
			shows = data.shows
			lastUpdated = moment.utc(data.lastUpdated)
		} else {
			shows = data
		}
		setup()
		
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
		$.getJSON(jsons['current'], function(data){
			currents = data;
			if (query !== ""){
				$('.search-input').val(query);
				resultsUpdate();
			} else {
				updateShowcase();
			}
		})
		
	}
	
	
	function updateShowList(showList, message){
		$('.results-container').empty();
		if (message){
			$('.results-container').append("<div class='result message'>"+ message + "</div>");
		}
		if (showList.length == 0){
			$('.results-container').append("<div class='result message'>Couldn't Find Any Streams</div>");
		} else {
			showList.forEach(function(show){
				var resultHtml = "<div class='result'><div class='result-name'>" + show.name;
				if (show.alt){
					resultHtml += "<div class='result-alt mobile-hide'>" + show.alt + "</div>"
				}
				resultHtml += "</div><div class='services-container'>";
				resultHtml += renderServices(show);
				resultHtml += "</div>";
				$('.results-container').append(resultHtml);
			})
		}
		$('.results-container').show();
		$('.showcase-container').hide();
		
		//console.log(showList);
	}
	function updateShowcase(){
		$('.showcase-container').empty();
		highlights.forEach(function(show){
			var showcaseHtml = "<div class='showcase-item'>";
			console.log(show.name)
			showcaseHtml += "<div class='showcase-art'><img src='" + popImg[show.name] + "'/></div>"
			showcaseHtml += "<div class='showcase-name'>" + show.name;
			if (show.alt){
				showcaseHtml += "<div class='showcase-alt mobile-hide'>" + show.alt + "</div>"
			}
			showcaseHtml += "</div><div class='showcase-services'>";
			showcaseHtml += renderServices(show);
			showcaseHtml += "</div>";
			$('.showcase-container').append(showcaseHtml);
		})
		$('.showcase-container').show();
		$('.results-container').hide();
	}
	
	function renderServices(show){
		var servicesHtml = "";
		providers[region].forEach(function(provider){
			if (show.sites[provider]){
				if (typeof show.sites[provider] === 'string' || show.sites[provider] instanceof String){
					servicesHtml += "<a href='" + show.sites[provider] + "' target='_blank'><div class='service service-" + provider + "' service='" + provider + "'>"
					if (currents[show.name]){
						if (typeof(currents[show.name]) === 'object' && Object.keys(currents[show.name]).length > 0 ){
							if (currents[show.name][region].indexOf(provider) < 0) { }
							else { servicesHtml += "<div class='simulcast'></div>" } 
						} else { servicesHtml += "<div class='simulcast'></div>" }
						
					}
					servicesHtml += "</div></a>"
				} else {
					servicesHtml += "<div class='service service-" + provider + "' service='" + provider + "'></div>"
				}
				
			} else {
				
			}
		})
		servicesHtml += "</div>";
		return servicesHtml;
	}
	
	var searchTimeout;
	$('.search-clear').on('click', function(){
		$('.search-input').val('');
		resultsUpdate();
		updateURL("");
		clearTimeout(searchTimeout);
	})
	
	
	
	$('.search-input').on('input', function(){
		clearTimeout(searchTimeout);
		resultsUpdate();
		//updateURL();
		searchTimeout = setTimeout(onSearchTimeout, 1000);
	})
	
	function onSearchTimeout(){
		var searchTerm = $('.search-input').val();
		ga('send', 'event', 'search', 'textbox', searchTerm, parseInt($(".result:not(.message)").length));
		updateURL(searchTerm);
	}
	
	function updateURL(searchTerm){
		var curSite = location.href.split("?")[0];
		if (searchTerm === '') {
			 history.replaceState(null, null, curSite);
		} else {
			history.replaceState(null, null,  curSite + "?q=" + searchTerm);
		}
	}
	function resultsUpdate(){
		if ($('.search-input').val() === '') { 
			$('.search-icon').show()
			$('.search-clear').hide()
			updateShowcase();
		} else if (providers[region].indexOf($('.search-input').val().toLowerCase()) > -1){ 
			$('.search-icon').hide()
			$('.search-clear').show()
			var providerIndex = providers[region].indexOf($('.search-input').val().toLowerCase());
			updateShowList(shows.filter(function(show){
				return providers[region][providerIndex] in show['sites']
			}))
		} else if ($('.search-input').val().toLowerCase() === 'current'){
			$('.search-icon').hide()
			$('.search-clear').show()
			updateShowList(shows.filter(function(show){
				return Object.keys(currents).indexOf(show['name']) > 0
			}))
		} else {
			$('.search-icon').hide()
			$('.search-clear').show()
			showshound.search($('.search-input').val(), updateShowList);
		}
	}
})