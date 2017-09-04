(function (global) {
	
	
	var event_map = {};
	
	
	var EThing = global.EThing || {};
	
	
	
	function returnTrue() {
		return true;
	}

	function returnFalse() {
		return false;
	}
	
	
	/*
	Event object
	*/
	
	EThing.Event = function( src, props ) {

		// Allow instantiation without the 'new' keyword
		if ( !( this instanceof EThing.Event ) ) {
			return new EThing.Event( src, props );
		}

		// Event type
		this.type = src;

		// Put explicitly provided properties onto the event object
		if ( props ) {
			EThing.utils.extend( this, props );
		}

		// Create a timestamp if incoming event doesn't have one
		this.timeStamp = Date.now();
		
	};

	EThing.Event.prototype = {
		constructor: EThing.Event,
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
				event = EThing.Event(event);
			
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
	
	/**
	 * register an handler to an event.
	 * @name on
	 * @memberof EThing
	 * @param {string} event event type string. Multiple space separated events can be given.
	 * @param {function(EThing.Event)} handler the function to be called when the event has been triggered.
	 */
	
	/**
	 * Remove an event handler.
	 * @name off
	 * @memberof EThing
	 * @param {string} event event type string. Multiple space separated events can be given.
	 * @param {function(EThing.Event)} [handler] A handler function previously attached for the event(s)
	 */
	
	/**
	 * register an handler to an event. The handler will be only executed once.
	 * @name one
	 * @memberof EThing
	 * @param {string} event event type string. Multiple space separated events can be given.
	 * @param {function(EThing.Event)} handler the function to be called when the event has been triggered.
	 */
	
	/**
	 * Execute all handlers attached for the given event type.
	 * @name trigger
	 * @memberof EThing
	 * @param {string|EThing.Event} event An event object instance or an event type string.
	 * @param {object} [extraParameters] Additional parameters to pass along to the event handler.
	 */
	
	
	/**
	 * @memberof EThing
	 * @event "ething.resource.removed"
	 */
	 
	/**
	 * @memberof EThing
	 * @event "ething.file.created"
	 */
	 
	/**
	 * @memberof EThing
	 * @event "ething.table.created"
	 */
	 
	/**
	 * @memberof EThing
	 * @event "ething.device.created"
	 */
	 
	/**
	 * @memberof EThing
	 * @event "ething.app.created"
	 */
	/**
	 * authenticated event.
	 *
	 * @memberof EThing
	 * @event "ething.authenticated"
	 */
	
	EventEngine(EThing);
	
	
	EThing.EventEngine = EventEngine;
	
	
})(this);
