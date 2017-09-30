(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ething', 'json!config.json'], factory);
    } else {
        // Browser globals
        factory(root.EThing,root.jQuery);
    }
}(this, function (EThing, config) {
	
	var UI = window.UI = window.UI || {};
	
	
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
		
		start: function(){
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
		connecting: false,
		
		state: 'disconnected',
		
		cache: {},
		
		cacheDelay: 1000,
		refreshDelay: 5000,
		inactivityDelay: 60000,
		
		mqttTopics: ["ething/signal/ResourceMetaUpdated","ething/signal/ResourceCreated","ething/signal/ResourceDeleted"],
		
		initialized: false,
		
		openWS: function(callback){
			var self = this;
			
			if(!this.wsClient){
				// Create a client instance
				try {
					this.wsClient = new Paho.MQTT.Client(config.mqtt.host || window.location.hostname, Number(config.mqtt.port || 1884), "web.js."+Math.round(Math.random()*100000));
				} catch(e){
					console.error(e);
					this.fail();
					return;
				}
				
				// set callback handlers
				this.wsClient.onConnectionLost = function(responseObject){
					self.onConnectionLostWS(responseObject);
				};
				this.wsClient.onMessageArrived = function(message){
					try {
						self.processWS(message);
					} catch(e) {
						console.error(e);
					}
				};
			}
			
			if(this.wsClient.isConnected() || this.connecting) return; // already connected !
			
			// connect the client
			try{
				this.connecting = true;
				console.log("[WS] connecting ...");
				
				var wsConnectConf = {
					onSuccess: function(){
						// Once a connection has been made, make a subscription and send a message.
						console.log("[WS] connected");
						
						// subscribing ...
						var dfrs = [];
						self.mqttTopics.forEach(function(topic){
							
							var dfr = EThing.utils.Deferred();
							dfrs.push(dfr);
							
							self.wsClient.subscribe(topic, {
								onSuccess: function(){
									console.log("[WS] subscribed to "+topic);
									dfr.resolve();
								},
								onFailure: function(responseObject){
									console.log("[WS] subscribe failure for topic " + topic + " : " + responseObject.errorMessage);
									dfr.reject(responseObject.errorMessage);
								}
							});
							
						});
						
						EThing.utils.Deferred.when.apply(EThing.utils.Deferred, dfrs).always(function(){
							self.connecting = false;
						}).done(function(){
							
							console.log("[WS] connected and subscribed");
							
							if(!EThing.arbo.lastRefreshTs || (Date.now() - EThing.arbo.lastRefreshTs > self.refreshDelay))
								EThing.arbo.refresh();
							
							if(typeof callback === 'function')
								callback(true);
						}).fail(function(err){
							self.closeWS();
							self.fail();
							
							if(typeof callback === 'function')
								callback(false);
						});
						
					},
					onFailure: function(responseObject){
						self.connecting = false;
						
						// Once a connection has been made, make a subscription and send a message.
						console.log("[WS] connection failure " + responseObject.errorMessage);
						
						if(typeof callback === 'function')
							callback(false);
						
						self.fail();
					}
				};
				
				if(typeof config.mqtt.password != 'undefined'){
					wsConnectConf.userName = config.mqtt.user;
					wsConnectConf.password = config.mqtt.password;
				}
				
				this.wsClient.connect(wsConnectConf);
				
			} catch(e){
				console.error(e);
				self.fail();
			}
			
		},
		
		processWS: function(message){
			var self = this;
			console.log("[WS] Message arrived: topic=" + message.destinationName);
			
			var signal = JSON.parse(message.payloadString);
			
			switch(signal.name){
				case 'ResourceMetaUpdated':
					var resourceId = signal.data.resource;
					var resource = EThing.arbo.findOneById(resourceId);
					var date = new Date(signal.ts*1000);
					if(!resource || date > resource.modifiedDate()){
						if(self.cache[resourceId]) clearTimeout(self.cache[resourceId]);
						self.cache[resourceId] = setTimeout(function(){
							delete self.cache[resourceId];
							console.log("[WS] updating resource " + resourceId);
							EThing.get(resourceId);
						},this.cacheDelay);
					}
					break;
				case 'ResourceCreated':
					var resourceId = signal.data.resource;
					var resource = EThing.arbo.findOneById(resourceId);
					if(!resource){
						if(self.cache[resourceId]) clearTimeout(self.cache[resourceId]);
						self.cache[resourceId] = setTimeout(function(){
							delete self.cache[resourceId];
							console.log("[WS] updating resource " + resourceId);
							EThing.get(resourceId);
						},this.cacheDelay);
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
				this.connecting = false;
				console.log("[WS] onConnectionLost:" + responseObject.errorMessage);
				console.log("[WS] auto reconnect ...");
				this.openWS();
			}
		},
		
		closeWS: function(){
			this.connecting = false;
			if(this.wsClient && this.wsClient.isConnected()){
				this.wsClient.disconnect();
				console.log("[WS] disconnect");
			}
		},
		
		started: false,
		
		start: function(){
			var self = this;
			
			if(this.started) return; // already started
			
			console.log('this.started = true;');
			this.started = true;
			
			if(this.closeTimeoutId) clearTimeout(this.closeTimeoutId);
			
			if(this.initialized===true){
				this.openWS();
			} else {
				// load the settings first !
				if(this.initialized!=="..."){
					
					console.log("[WS] initializing...");
					this.initialized = '...';
					
					require(['mqttws'], function(){
						console.log("[WS] lib Paho.MQTT.Client loaded");
						
						self.initialized = true;
						
						if(self.started)
							self.openWS();
					}, function(){
						console.log("[WS] fail initialization, unable to fetch Paho.MQTT.Client lib");
						self.fail();
					});
					
				}
				
			}
		},
		
		stop: function(){
			var self = this;
			console.log('this.started = false;');
			this.started = false;
			// close the socket only after a period of inactivity !
			this.closeTimeoutId = setTimeout(function(){
				delete self.closeTimeoutId;
				self.closeWS();
			}, this.inactivityDelay);
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
		
		onFailure: null,
		
		fail: function(){
			console.log("[WS] fail");
			this.started = false;
			this.closeWS();
			if(this.closeTimeoutId) clearTimeout(this.closeTimeoutId);
			
			if(typeof this.onFailure === 'function') this.onFailure();
		}
		
	};





	var RefreshStrategy = {
		strategy: null,
		state: 'stopped',
		enabled: true,
		
		isStarted: function(){
			return this.state === 'started';
		},
		isStopped: function(){
			return this.state === 'stopped';
		},
		
		start: function(){
			if(this.enabled && this.isStopped()){
				console.log("[UI] RefreshStrategy => start");
				this.state = 'started';
				if(this.strategy) this.strategy.start();
			}
		},
		
		stop: function(){
			if(this.enabled && this.isStarted()){
				console.log("[UI] RefreshStrategy => stop");
				this.state = 'stopped';
				if(this.strategy) this.strategy.stop();
			}
		},
		
		disable: function(){
			if(!this.isEnabled()){
				console.log("[UI] RefreshStrategy => disable");
				this.stop();
				this.enabled = false;
			}
		},
		
		enable: function(){
			if(!this.isEnabled()){
				console.log("[UI] RefreshStrategy => enable");
				this.enabled = true;
				this.start();
			}
		},
		
		isEnabled: function(){
			return this.enabled;
		},
		
		setStrategy: function(strategy){
			this.strategy = strategy;
			if(this.isStarted()){
				this.start();
			}
		}
	};


	if(config.mqtt && WsRefreshStrategy.isCompatible()){
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
	
	
	/* stop the refresh when the tab is not visible ! */
	
	// Set the name of the hidden property and the change event for visibility
	var hidden, visibilityChange; 
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
		RefreshStrategy.stop();
	  } else {
		RefreshStrategy.start();
	  }
	}

	// Warn if the browser doesn't support addEventListener or the Page Visibility API
	if (!(typeof document.addEventListener === "undefined" || typeof document[hidden] === "undefined")) {
		
	  // Handle page visibility change
	  document.addEventListener(visibilityChange, handleVisibilityChange, false);

	}
	
	
	UI.startRefresh = function(){
		RefreshStrategy.start();
	};
	UI.stopRefresh = function(){
		RefreshStrategy.stop();
	};
	UI.enableRefresh = function(){
		RefreshStrategy.enable();
	};
	UI.disableRefresh = function(){
		RefreshStrategy.disable();
	};
	

	return UI
	
}));