(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ething', 'mqttws'], factory);
    } else {
        // Browser globals
        factory(root.EThing,root.jQuery);
    }
}(this, function (EThing) {


	var PollingRefreshStrategy = {
		/* polling strategy */
			
		timerId: null,
		timerType: null,
		interval: 60000,
		lastTime: null,
		paused: false,
		processing: function(){
			this.lastTime = Date.now();
			EThing.arbo.refresh(); // refresh the arbo
		},
		
		start: function(nodelay){
			this.paused = false;
			if(!this.isEnabled()){
				var self = this;
				var delay = self.interval;
				
				if(EThing.arbo.lastRefreshTs){
					var diff = Date.now() - EThing.arbo.lastRefreshTs;
					if(diff > self.interval){
						delay = 1;
					} else {
						delay = this.interval - diff;
					}
				}
				
				if(!!nodelay) delay = 1;
								
				self.timerType = 'timeout';
				self.timerId = setTimeout(function(){
					
					self.processing();
					
					self.timerType = 'interval';
					self.timerId = setInterval( function(){
						self.processing();
					}, self.interval);
				}, delay);
			}
		},
		
		stop: function(){
			if(this.isEnabled()){
				this.timerType === 'timeout' ? clearTimeout(this.timerId) : clearInterval(this.timerId);
				this.timerId = null;
				this.timerType = null;
				this.paused = false;
			}
		},
		
		pause: function(){
			if(this.isEnabled()){
				this.stop();
				this.paused = true;
			}
		},
		
		resume: function(){
			if(this.paused){
				this.start();
			}
		},
		
		isEnabled: function(){
			return !!this.timerId;
		}
	};



	var WsRefreshStrategy = {
		
		wsClient: null,
			
		openWS: function(callback){
			var self = this;
			
			if(!this.wsClient){
				// Create a client instance
				this.wsClient = new Paho.MQTT.Client(window.location.hostname, Number(1884), "web.js."+Math.round(Math.random()*100000));
				
				// set callback handlers
				this.wsClient.onConnectionLost = this.onConnectionLostWS;
				this.wsClient.onMessageArrived = this.processWS;
			}
			
			if(this.wsClient.isConnected()) return; // already connected !
			
			// connect the client
			try{
				this.wsClient.connect({
					onSuccess: function(){
						// Once a connection has been made, make a subscription and send a message.
						console.log("[WS] connected");
						self.wsClient.subscribe("ething/signal/#", {
							onSuccess: function(){
								
								if(!EThing.arbo.lastRefreshTs || (Date.now() - EThing.arbo.lastRefreshTs > 5000))
									EThing.arbo.refresh();
							},
							onFailure: function(){
								self.closeWS();
								if(typeof self.onFailure === 'function') self.onFailure();
							}
						});
						
						if(typeof callback === 'function')
							callback(true);
					},
					onFailure: function(responseObject){
						// Once a connection has been made, make a subscription and send a message.
						console.log("[WS] connection failure " + responseObject.errorMessage);
						
						if(typeof callback === 'function')
							callback(false);
						
						if(typeof self.onFailure === 'function') self.onFailure();
					}
				});
			} catch(e){}
			
		},
		
		processWS: function(message){
			console.log("[WS] Message arrived: topic=" + message.destinationName);
			
			var signal = JSON.parse(message.payloadString);
			
			switch(signal.name){
				case 'ResourceMetaUpdated':
					var resourceId = signal.data.resource;
					var resource = EThing.arbo.findOneById(resourceId);
					var date = new Date(signal.ts*1000);
					if(!resource || date > resource.modifiedDate()){
						console.log("[WS] updating resource " + resourceId);
						EThing.get(resourceId);
					}
					break;
				case 'ResourceCreated':
					var resourceId = signal.data.resource;
					var resource = EThing.arbo.findOneById(resourceId);
					if(!resource){
						console.log("[WS] updating resource " + resourceId);
						EThing.get(resourceId);
					}
					break;
				case 'ResourceDeleted':
					var resourceId = signal.data.resource;
					EThing.arbo.remove(resourceId);
					break;
			}
			
		},
		
		onConnectionLostWS: function (responseObject) {
			if (responseObject.errorCode !== 0) {
				console.log("[WS] onConnectionLost:" + responseObject.errorMessage);
				console.log("[WS] auto reconnect ...");
				WsRefreshStrategy.openWS();
			}
		},
		
		closeWS: function(){
			if(this.wsClient && this.wsClient.isConnected()){
				this.wsClient.disconnect();
				console.log("[WS] disconnect");
			}
		},
		
		
		start: function(){
			if(this.closeTimeoutId) clearTimeout(this.closeTimeoutId);
			
			this.openWS();
		},
		
		stop: function(){
			var self = this;
			// close the socket only after a period of inactivity !
			this.closeTimeoutId = setTimeout(function(){
				delete self.closeTimeoutId;
				self.closeWS();
			}, 60000);
		},
		
		isCompatible: function(){
			// Check dependencies are satisfied in this browser.
			if (!("WebSocket" in window && window["WebSocket"] !== null)) {
				return false;
			}
			if (!("localStorage" in window && window["localStorage"] !== null)) {
				return false;
			}
			if (!("ArrayBuffer" in window && window["ArrayBuffer"] !== null)) {
				return false;
			}
			
			return true;
		},
		
		onFailure: null
		
	};





	var RefreshStrategy = {
		strategy: null,
		state: 'stopped',
		
		start: function(){
			console.log("[UI] RefreshStrategy => start");
			this.state = 'started';
			if(this.strategy) this.strategy.start();
		},
		
		stop: function(){
			console.log("[UI] RefreshStrategy => stop");
			this.state = 'stopped';
			if(this.strategy) this.strategy.stop();
		},
		
		setStrategy: function(strategy){
			this.strategy = strategy;
			if(this.state === 'started'){
				if(this.strategy) this.strategy.start();
			}
		}
	};


	if(WsRefreshStrategy.isCompatible()){
		console.log("[UI] RefreshStrategy => ws/mqtt");
		RefreshStrategy.strategy = WsRefreshStrategy;
		WsRefreshStrategy.onFailure = function(){
			// fall back to the polling strategy
			console.log("[UI] RefreshStrategy => polling");
			RefreshStrategy.setStrategy(PollingRefreshStrategy);
		}
	} else {
		console.log("[UI] RefreshStrategy => polling");
		RefreshStrategy.startegy = PollingRefreshStrategy;
	}


	return RefreshStrategy
	
}));