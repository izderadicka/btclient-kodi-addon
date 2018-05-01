//console.log('#Loading a web page');
var page = require('webpage').create(),
	system = require('system');
	var url = system.args[1];
if (!url) {
	console.error('No URL provided');
	phantom.exit(1);
}

page.settings.resourceTimeout = 60000;

function waitFor(testFx, onReady, timeOutMillis) {
    var maxtimeOutMillis = timeOutMillis ? timeOutMillis : 3000, // < Default
																	// Max
																	// Timout is
																	// 3s
        start = new Date().getTime(),
        condition = false,
        interval = setInterval(function() {
            if ( (new Date().getTime() - start < maxtimeOutMillis) && !condition ) {
                // If not time-out yet and condition not yet fulfilled
                condition = testFx();
            } else {
                if(!condition) {
                    // If condition still not fulfilled (timeout but condition
					// is 'false')
					console.error("Processing timeout");
                    phantom.exit(3);
                } else {
                    // Condition fulfilled (timeout and/or condition is 'true')
                    onReady();
                    clearInterval(interval); // < Stop this interval
                }
            }
        }, 100); 
}


page.open(url, function (status) {
  
  if (status !== 'success') {
	  console.error('Page failed to load: '+ status);
	  phantom.exit(4);
  }
  
  //console.log('#PageLoaded '+status);
  waitFor(
		// test that page is loaded
		  function() {
			  return page.evaluate(
			  function(){
				  return $('div.search-result').hasClass('loaded');
			  });
  			},
  			// do action
  			function() {
		      var result = page.evaluate(function() {
			  var result = [];
			  var base = $('div.search-result');
			  if (base.hasClass('loaded')) {
				  $('.item', base).each(function(idx, item) {
					  var getText = function(cls) {
						  return $(cls,item).parent().contents()
						  .filter(function() { return this.nodeType == Node.TEXT_NODE; }).text().trim();
					  };
					  var link = $('div.name a', item);
					  var size = getText('.fi-database');
					  var length = getText('.fi-clock-o');
					  var img = $('div.img img', item).attr('src');
					  var locked =$('.lock', item).length
					  if (!locked) {
						  result.push({url: link.attr('href'), 
							  			name:link.text(),
							  			size: size,
							  			legth: length,
							  			img : img
							  			});
					  }
				  	});
				  return result;

			  	} 
		      });
		      if (result) {
		    	  console.log(JSON.stringify(result));
		    	  phantom.exit();
		      } else {
		    	  console.error('Something went wrong in page script');
		    	  phantom.exit(2);
		      }
  			},
  			// timeout
  			15000
  			);
});