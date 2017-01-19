var page = require('webpage').create();
page.viewportSize = {width: 3000, height: 3000};
page.paperSize = { width: 1024, height: 768, border: '0px' }
page.open('https://www.meteoblue.com/en/weather/forecast/seeing/cheorwon-eup_republic-of-korea_1845385', function() {

	var clipRect = page.evaluate(function(){
		return document.querySelector('.table-seeing').getBoundingClientRect();
	});

	page.clipRect = {
		top: clipRect.top,
		left: clipRect.left,
		width: clipRect.width,
		height: clipRect.height
	};
	setTimeout(function() {
		page.render('images/seeing-cherwon.png');
		phantom.exit();
	}, 1000);
});