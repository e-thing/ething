(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define([], factory);
    }
}(this, function () {
	
	var UI = window.UI = window.UI || {};
	
	
	
	function returnTrue() {
		return true;
	}

	function returnFalse() {
		return false;
	}
	
	
	/*
	Event object
	*/
	
	var Event = function( src, props ) {

		// Allow instantiation without the 'new' keyword
		if ( !( this instanceof Event ) ) {
			return new Event( src, props );
		}

		// Event type
		this.type = src;

		// Put explicitly provided properties onto the event object
		if ( props ) {
			for(var i in props){
				this[i] = props[i];
			}
		}

		// Create a timestamp if incoming event doesn't have one
		this.timeStamp = Date.now();
		
	};

	Event.prototype = {
		constructor: Event,
		isDefaultPrevented: returnFalse,
		isPropagationStopped: returnFalse,
		isImmediatePropagationStopped: returnFalse,

		preventDefault: function() {
			this.isDefaultPrevented = returnTrue;
		},
		stopPropagation: function() {
			this.isPropagationStopped = returnTrue;
		},
		stopImmediatePropagation: function() {
			this.isImmediatePropagationStopped = returnTrue;
			this.stopPropagation();
		}
	};
	
	
	function EventEngine(obj){
		
		var event_map = {};
		
		obj.on = function(events, handler) {
			if(typeof handler == 'function'){
				events = events.split(' ');
				for(var i=0; i<events.length; i++){
					var event = events[i];
					if(event.length){
						if(!event_map[event]) event_map[event] = [];
						event_map[event].push(handler);
					}
				}
			}
		}
		
		obj.off = function(events, handler) {
			events = events.split(' ');
			for(var i=0; i<events.length; i++){
				var event = events[i];
				if(event.length){
					if(typeof handler == 'function'){
						for(var j=0; i<event_map[event].length; i++){
							if(event_map[event][j]===handler){
								event_map[event].splice(j, 1);
								j--;
							}
						}
					}
					else {
						event_map[event] = [];
					}
				}
			}
		}
		
		obj.one = function(events, handler) {
			if(typeof handler == 'function'){
				obj.on(events, function(){
					obj.off(events,handler);
					handler.apply(this,Array.prototype.slice.call(arguments));
				});
			}
		}
		
		obj.trigger = function(event, extraParameters){
			if(typeof event === 'string')
				event = Event(event);
			
			var type = event.type,
				h = event_map[type] || [];
			
			for(var i=0; i<h.length; i++){
				var args = [event];
				if(Array.isArray(extraParameters))
					args = args.concat(extraParameters);
				h[i].apply(obj,args);
				
				if(event.isImmediatePropagationStopped() || event.isPropagationStopped())
					break;
			}
			return event;
		}
		
		
	}
	
	EventEngine(UI);
	
	
	return UI;
	
}));