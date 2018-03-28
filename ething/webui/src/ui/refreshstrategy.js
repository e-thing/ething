(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ething'], factory);
    }
}(this, function (EThing) {
	
	
	// server sent event
	var SSE = {
		
		source: null,
		
		start: function(){
			
			var source = this.source = new EventSource("/api/events"),
				self = this;
			
			/*source.onopen = function() {
				console.log("opened");
			};*/
			
			source.onmessage = function(event) {
				var data = JSON.parse(event.data);
				dispatch(data);
			};
			
			
		},
		
		stop: function(){
			if(this.source) this.source.close();
		}
		
		
	};
	
	
	var cache = {};
	
	var cacheDelay = 200;
	
	var fetch = function(resourceId){
		if(cache[resourceId]) clearTimeout(cache[resourceId]);
		cache[resourceId] = setTimeout(function(){
			delete cache[resourceId];
			console.log("updating resource " + resourceId);
			EThing.get(resourceId);
		},cacheDelay);
	}
	
	/*
	{"data": {"ts": 1521191880.559514}, "name": "Timer", "ts": 1521191880.559627}
	*/
	var dispatch = function(event){
		//console.log(event);
		
		var name = event.name,
			isResourceEvent = !!event.data.resource,
			resource,
			evt = EThing.Event(name, {
				data: event.data,
				originalEvent: event
			});
		
		if(isResourceEvent){
			resource = EThing.arbo.findOneById(event.data.resource);
			
			var resourceId = event.data.resource;
			
			switch(name){
				case 'ResourceMetaUpdated':
					var mtime = new Date(event.data.rModifiedDate);
					if(!resource || mtime > resource.modifiedDate()){
						fetch(resourceId);
					}
					break;
				case 'ResourceCreated':
					if(!resource){
						fetch(resourceId);
					}
					break;
				case 'ResourceDeleted':
					EThing.arbo.remove(resourceId);
					break;
			}
			
			if(resource){
				resource.trigger(evt);
			}
			
		} else {
			EThing.trigger(evt);
		}
		
	}
	
	
	
	
	/* stop the refresh when the tab is not visible ! */
	
	// Set the name of the hidden property and the change event for visibility
	/*var hidden, visibilityChange; 
	if (typeof document.hidden !== "undefined") { // Opera 12.10 and Firefox 18 and later support 
	  hidden = "hidden";
	  visibilityChange = "visibilitychange";
	} else if (typeof document.msHidden !== "undefined") {
	  hidden = "msHidden";
	  visibilityChange = "msvisibilitychange";
	} else if (typeof document.webkitHidden !== "undefined") {
	  hidden = "webkitHidden";
	  visibilityChange = "webkitvisibilitychange";
	}
	
	function handleVisibilityChange() {
	  if (document[hidden]) {
		//RefreshStrategy.stop();
	  } else {
		//RefreshStrategy.start();
	  }
	}

	// Warn if the browser doesn't support addEventListener or the Page Visibility API
	if (!(typeof document.addEventListener === "undefined" || typeof document[hidden] === "undefined")) {
		
	  // Handle page visibility change
	  document.addEventListener(visibilityChange, handleVisibilityChange, false);

	}*/
	
	SSE.start();
	

	return SSE
	
}));