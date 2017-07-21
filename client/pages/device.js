(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['js/ui', 'jquery', 'ething', 'marked', 'form', 'highlight', 'css!./device', 'css!font-awesome'], factory);
    }
}(this, function (UI, $, EThing, marked) {
	
	
	
	/* mysensors stuff */
	var objectValues = function(obj){
		var arr = [];
		for(var i in obj){
			arr.push(obj[i]);
		}
		return arr;
	}
	
	var findKey = function(obj, value){
		for(var i in obj){
			if(value === obj[i]) return i;
		}
	}
	
	var MySensors_messageTypes = {
		'PRESENTATION'  : 0,
		'SET'  : 1,
		'REQ'  : 2,
		'INTERNAL'  : 3,
		'STREAM'  : 4
	};
	
	var MySensors_sensorTypes = {
		'S_DOOR'  : 0 ,
		'S_MOTION'  : 1 ,
		'S_SMOKE'  : 2 ,
		'S_BINARY'  : 3 ,
		//'S_LIGHT'  : 3 ,
		'S_DIMMER'  : 4 ,
		'S_COVER'  : 5 ,
		'S_TEMP'  : 6 ,
		'S_HUM'  : 7 ,
		'S_BARO'  : 8 ,
		'S_WIND'  : 9 ,
		'S_RAIN'  : 10,
		'S_UV'  : 11,
		'S_WEIGHT'  : 12,
		'S_POWER'  : 13,
		'S_HEATER'  : 14,
		'S_DISTANCE'  : 15,
		'S_LIGHT_LEVEL'  : 16,
		'S_ARDUINO_NODE'  : 17,
		'S_ARDUINO_REPEATER_NODE'  : 18,
		'S_LOCK'  : 19,
		'S_IR'  : 20,
		'S_WATER'  : 21,
		'S_AIR_QUALITY'  : 22,
		'S_CUSTOM'  : 23,
		'S_DUST'  : 24,
		'S_SCENE_CONTROLLER'  : 25,
		'S_RGB_LIGHT'  : 26,
		'S_RGBW_LIGHT'  : 27,
		'S_COLOR_SENSOR'  : 28,
		'S_HVAC'  : 29,
		'S_MULTIMETER'  : 30,
		'S_SPRINKLER'  : 31,
		'S_WATER_LEAK'  : 32,
		'S_SOUND'  : 33,
		'S_VIBRATION'  : 34,
		'S_MOISTURE'  : 35,
		'S_INFO'  : 36,
		'S_GAS'  : 37,
		'S_GPS'  : 38,
		'S_WATER_QUALITY'  : 39,
		'S_UNK'  : 9999
	};
	
	var MySensors_valueTypes = {
		'V_TEMP'  : 0 ,
		'V_HUM'  : 1 ,
		'V_STATUS'  : 2 ,
		'V_LIGHT'  : 2 ,
		'V_PERCENTAGE'  : 3 ,
		'V_DIMMER'  : 3 ,
		'V_PRESSURE'  : 4 ,
		'V_FORECAST'  : 5 ,
		'V_RAIN'  : 6 ,
		'V_RAINRATE'  : 7 ,
		'V_WIND'  : 8 ,
		'V_GUST'  : 9 ,
		'V_DIRECTION'  : 10,
		'V_UV'  : 11,
		'V_WEIGHT'  : 12,
		'V_DISTANCE'  : 13,
		'V_IMPEDANCE'  : 14,
		'V_ARMED'  : 15,
		'V_TRIPPED'  : 16,
		'V_WATT'  : 17,
		'V_KWH'  : 18,
		'V_SCENE_ON'  : 19,
		'V_SCENE_OFF'  : 20,
		'V_HVAC_FLOW_STATE'  : 21,
		'V_HVAC_SPEED'  : 22,
		'V_LIGHT_LEVEL'  : 23,
		'V_VAR1'  : 24,
		'V_VAR2'  : 25,
		'V_VAR3'  : 26,
		'V_VAR4'  : 27,
		'V_VAR5'  : 28,
		'V_UP'  : 29,
		'V_DOWN'  : 30,
		'V_STOP'  : 31,
		'V_IR_SEND'  : 32,
		'V_IR_RECEIVE'  : 33,
		'V_FLOW'  : 34,
		'V_VOLUME'  : 35,
		'V_LOCK_STATUS'  : 36,
		'V_LEVEL'  : 37,
		'V_VOLTAGE'  : 38,
		'V_CURRENT'  : 39,
		'V_RGB'  : 40,
		'V_RGBW'  : 41,
		'V_ID'  : 42,
		'V_UNIT_PREFIX'  : 43,
		'V_HVAC_SETPOINT_COOL'  : 44,
		'V_HVAC_SETPOINT_HEAT'  : 45,
		'V_HVAC_FLOW_MODE'  : 46,
		'V_TEXT'  : 47,
		'V_CUSTOM'  : 48,
		'V_POSITION'  : 49,
		'V_IR_RECORD'  : 50,
		'V_PH'  : 51,
		'V_ORP'  : 52,
		'V_EC'  : 53,
		'V_VAR'  : 54,
		'V_VA'  : 55,
		'V_POWER_FACTOR'  : 56
	};
	
	var MySensors_internalTypes = {
		'I_BATTERY_LEVEL'  : 0,
		'I_TIME'  : 1,
		'I_VERSION'  : 2,
		'I_ID_REQUEST'  : 3,
		'I_ID_RESPONSE'  : 4,
		'I_INCLUSION_MODE'  : 5,
		'I_CONFIG'  : 6,
		'I_FIND_PARENT'  : 7,
		'I_FIND_PARENT_RESPONSE'  : 8,
		'I_LOG_MESSAGE'  : 9,
		'I_CHILDREN'  : 10,
		'I_SKETCH_NAME'  : 11,
		'I_SKETCH_VERSION'  : 12,
		'I_REBOOT'  : 13,
		'I_GATEWAY_READY'  : 14,
		'I_SIGNING_PRESENTATION'  : 15,
		'I_NONCE_REQUEST'  : 16,
		'I_NONCE_RESPONSE'  : 17,
		'I_HEARTBEAT_REQUEST'  : 18,
		'I_PRESENTATION'  : 19,
		'I_DISCOVER_REQUEST'  : 20,
		'I_DISCOVER_RESPONSE'  : 21,
		'I_HEARTBEAT_RESPONSE'  : 22,
		'I_LOCKED'  : 23,
		'I_PING'  : 24,
		'I_PONG'  : 25,
		'I_REGISTRATION_REQUEST'  : 26,
		'I_REGISTRATION_RESPONSE'  : 27,
		'I_DEBUG'  : 28
	};
	
	var MySensors_streamTypes = {
		'ST_FIRMWARE_CONFIG_REQUEST'  : 0,
		'ST_FIRMWARE_CONFIG_RESPONSE'  : 1,
		'ST_FIRMWARE_REQUEST'  : 2,
		'ST_FIRMWARE_RESPONSE'  : 3,
		'ST_SOUND'  : 4,
		'ST_IMAGE'  : 5
	};
	
	
	/* helpers */
	
	var supportsAudioPlayback = function(contentType){
	  var audioElement = document.createElement('audio');
	  return !!(audioElement.canPlayType && audioElement.canPlayType(contentType).replace(/no/, ''));
	};
	
	var supportsVideoPlayback = function(contentType){
	  var videoElement = document.createElement('video');
	  return !!(videoElement.canPlayType && videoElement.canPlayType(contentType).replace(/no/, ''));
	};
	
	var blobToText = function(blob, cb){
		if(blob instanceof Blob){
			var reader = new window.FileReader();
			reader.readAsText(blob);
			reader.onloadend = function() {
				cb(reader.result);
			};
		} else {
			cb(blob);
		}
	};
	
	var highlight = function($el){
		if($el) $el.find('code').each(function(i, block) {
			hljs.highlightBlock(block);
		});
	};
	
	var markdown = function(element){
		var $element = $(element);
		if($element.length) {
			var content = $(element).text();
			if(content)
				$element[0].innerHTML = marked(content, {
					gfm: true,
					tables: true,
					breaks: true,
					highlight: function (code, lang ) {
						var hc = hljs.highlightAuto(code,lang ? [lang] : undefined);
						return hc.value;
					}
				});
		}
	}
	
	
	var createView = function(parametersForm, executeEngine){
		
		var $parameters = $('<div class="operation-body-parameters"></div>');
		var $toolbar = $(
			'<div class="operation-body-toolbar">'+
				'<button type="button" class="operation-body-toolbar-execute btn btn-primary">Execute !</button>'+
				'<button type="button" class="operation-body-toolbar-hide btn btn-link">Hide Response</button>'+
			'</div>'
		);
		var $result = $('<div class="operation-body-result"></div>');
		
		
		// parameters
		var hasFormParameters = (parametersForm && ( !(parametersForm instanceof $.Form.Layout) || parametersForm.length() ) );
		if(hasFormParameters)
			$parameters.form(parametersForm);
		else
			$parameters.hide();
		
		
		var updateTb = function(){
			$toolbar.find('.operation-body-toolbar-hide').toggle(
				$result.is(':visible:not(:empty)')
			);
		};
		
		var success = function($view){
			$view.addClass('operation-body-result-view');
			$result.empty().addClass('success').html($view).slideDown(updateTb);
		};
		
		var error = function(err){
			// error
			console.error('failed with the following: ', err);
			
			$result.empty().addClass('error');
			$result.text('failed with the following: '+String(err));
			$result.slideDown(updateTb);
		};
		
		// execution
		$toolbar.find('.operation-body-toolbar-execute').click(function(){
			
			var paramDfr = hasFormParameters ? $parameters.form('submit') : $.Deferred().resolve({});
			
			paramDfr.done(function(parameters){
				
				$result.empty().removeClass('success error').html('loading ...');
				
				executeEngine.execute(parameters, success, error);
				
			});
			
		});
		
		$toolbar.find('.operation-body-toolbar-hide').click(function(){
			$result.filter(':visible').empty().slideUp(updateTb);
		});
		
		updateTb();
		
		return [$parameters, $toolbar, $result];
	};
	
	
	
	
	
	var OperationView = function(device, operationApi){
		this.device = device;
		this.operationApi = operationApi;
	}
	
	OperationView.prototype.execute = function( parameters, success, error){
		
		var contentType = this.operationApi.response,
			self = this;
		
		// MJPEG
		if (/^multipart\/x-mixed-replace/.test(contentType) || contentType=='video/x-motion-jpeg' || contentType=='video/x-jpeg') {
		  success( $('<img>').attr('src', this.toUrl(parameters)) );
		}
		else if (/^audio\//.test(contentType) && supportsAudioPlayback(contentType)) {
		  success( $('<audio controls>').append($('<source>').attr('src', this.toUrl(parameters)).attr('type', contentType)) );
		}
		else if (/^video\//.test(contentType)) {
			if(supportsVideoPlayback(contentType)){
				success( $('<video controls autoplay>').append($('<source>').attr('src', this.toUrl(parameters)).attr('type', contentType)) );
			} else {
				// flv ...
				var src = this.toUrl(parameters);
				success( $('<object width="425" height="300" class="videoplayer" data="http://releases.flowplayer.org/swf/flowplayer-3.2.18.swf" type="application/x-shockwave-flash"><param name="movie" value="http://releases.flowplayer.org/swf/flowplayer-3.2.18.swf" /><param name="allowfullscreen" value="true" /><param name="allowscriptaccess" value="always" /><param name="flashvars" value=\'config={"clip":{"url":"'+src+'"},"playlist":[{"url":"'+src+'"}]}\' /></object>') );
			}
		}
		else {
			
			// get the content as Blob
			
			this.getData(parameters).done(function(blobData){
				
				var contentType = blobData.type;
				
				
				if (!blobData || blobData.size == 0) {
					success( $('<div>').text('no content') );
				  // JSON
				} else if (/json/.test(contentType)) {
					
					blobToText(blobData, function(data){
						var $view = $('<pre/>');
						try {
							data = JSON.stringify(JSON.parse(data), null, '  '); // make it beautiful
							$view.addClass('json');
						} catch (_error) {
							data = 'can\'t parse JSON.  Raw result:\n\n' + data;
							$view.addClass('nohighlight');
						}
						
						$view.append( $('<code />').text(data) );
						highlight($view);
						
						success($view);
					});

				  // HTML
				} else if (contentType === 'text/html') {
					
					blobToText(blobData, function(data){
						var $view = $('<pre class="html"/>').append( $('<code />').text(data) );
						highlight($view);
						
						success($view);
					});
					
				  // xml
				} else if (/xml/.test(contentType)) {
					
					blobToText(blobData, function(data){
						var $view = $('<pre class="xml"/>').append( $('<code />').text(data) );
						highlight($view);
						
						success($view);
					});
					
				  // Plain Text
				} else if (/text\/plain/.test(contentType)) {
					
					blobToText(blobData, function(data){
						var $view = $('<pre class="plain"/>').append( $('<code />').text(data) );
						highlight($view);
						
						success($view);
					});
					
				  // Image
				} else if (/^image\//.test(contentType)) {
					
					// build an image from the blob data
					var imageUrl = ( window.URL || window.webkitURL).createObjectURL( blobData );
					var image = new Image();
					image.src = imageUrl;
					success( $(image) );
					
				  // Audio
				} else if (/^audio\//.test(contentType) && supportsAudioPlayback(contentType)) {
					success( $('<audio controls>').append($('<source>').attr('src', self.toUrl(parameters)).attr('type', contentType)) );

				  // video
				} else if (/^video\//.test(contentType)) {
					if(supportsVideoPlayback(contentType)){
						success( $('<video controls autoplay>').append($('<source>').attr('src', this.toUrl(parameters)).attr('type', contentType)) );
					} else {
						// flv ...
						var src = this.toUrl(parameters);
						success( $('<object width="425" height="300" class="videoplayer" data="http://releases.flowplayer.org/swf/flowplayer-3.2.18.swf" type="application/x-shockwave-flash"><param name="movie" value="http://releases.flowplayer.org/swf/flowplayer-3.2.18.swf" /><param name="allowfullscreen" value="true" /><param name="allowscriptaccess" value="always" /><param name="flashvars" value=\'config={"clip":{"url":"'+src+'"},"playlist":[{"url":"'+src+'"}]}\' /></object>') );
					}
				} else {
					
					error( new Error('unable to display the response') );
				}
				
				
			}).fail(function(err){
				error(err);
			});
			
			
		}
		
		
	}
	
	OperationView.prototype.toUrl = function( parameters ){
		
		var url = 'devices/'+this.device.id()+'/call/'+this.operationApi.name;
		
		if(parameters && !$.isEmptyObject(parameters)){
			
			var jsonStr = JSON.stringify(parameters);
			
			url += '?paramData='+ encodeURIComponent(jsonStr);
		}
		
		return EThing.toApiUrl(url,true);
	}
	
	OperationView.prototype.getData = function( parameters ){
		return this.device.execute(this.operationApi.name, parameters, true);
	}
	
	
	
	
	
	
	
	
	
	
	var DeviceViewer = function(element, options){
		var self = this,
			descriptionMaxHeight = 150;
		
	
		if(options instanceof EThing.Device)
			options = {
				device: options
			};
		
		this.device = options.device;
		this.$element = $(element);
		this.options = options;
		
		
		// view 
		this.$element.empty().html(
			'<div class="info">'+
				'<div class="page-header">'+
				  '<h1 class="info-title"></h1>'+
				'</div>'+
				'<div>'+
					'<div class="widget"></div>'+
					'<div class="info-meta"></div>'+
					'<div style="clear: both;"></div>'+
				'</div>'+
				'<div class="info-description"></div>'+
			'</div>'+
			'<div class="api">'+
				'<h4>API</h4>'+
				'<div class="content">loading...</div>'+
			'</div>'+
			'<div class="data">'+
				'<h4>DATA</h4>'+
				'<div class="content">loading...</div>'+
			'</div>'+
			'<div class="resources">'+
				'<h4>RESOURCES</h4>'+
				'<div class="content"></div>'+
			'</div>'+
			'<div class="apikey">'+
				'<h4>API KEY</h4>'+
				'<p><a href="#!developer">Click here</a> to get the API KEY for this device</p>'+
			'</div>'+
			'</div>'
		);
		
		this.$element.find('.resources, .data, .apikey').hide();
		
		var $editBtn = $('<button type="button" class="btn btn-link btn-xs"><span class="glyphicon glyphicon-cog" aria-hidden="true"></span><span class="hidden-xs"> edit</span></button>').click(function(){
			UI.go('resource',{
				rid: self.device.id()
			});
		});
		
		// title
		this.$element.find('.info-title').html(this.device.name()+' <small>[id:'+this.device.id()+']</small>').append($editBtn);
		
		// meta
		var $meta = this.$element.find('.info-meta');
		
		// battery
		var batIcon;
		var batteryValue = this.device.battery();
		if(batteryValue === null) batIcon = 'plug';
		else if(batteryValue < 12.5) batIcon = 'battery-empty';
		else if(batteryValue < 37.5) batIcon = 'battery-quarter';
		else if(batteryValue < 62.5) batIcon = 'battery-half';
		else if(batteryValue < 87.5) batIcon = 'battery-three-quarters';
		else batIcon = 'battery-full';
		$('<div class="info-meta-item">').addClass('ellipsis').html('<i class="fa fa-'+batIcon+'" aria-hidden="true"></i> '+(typeof batteryValue == 'number' ? batteryValue+"%" : 'no battery')).appendTo($meta);
		
		// last time the device communicate
		var lastSeenDateValue = this.device.lastSeenDate();
		$('<div class="info-meta-item">').addClass('ellipsis').html('<span class="glyphicon glyphicon-time" aria-hidden="true"></span> '+(lastSeenDateValue ? UI.dateToString(lastSeenDateValue) : 'never')).appendTo($meta);
		
		// location
		var location = this.device.location();
		var parts = [];
		if(location){
			if( typeof location.latitude != 'undefined' && typeof location.longitude != 'undefined')
				parts.push( location.latitude+"N "+location.longitude+"E" );
			if( typeof location.place != 'undefined' ) parts.push(location.place);
			if( typeof location.floor != 'undefined' ) parts.push('floor:'+location.floor);
			if( typeof location.room != 'undefined' ) parts.push(location.room);
		}
		var locationStr = parts.length ? parts.join(',') : 'somewhere on earth';
		$('<div class="info-meta-item">').addClass('ellipsis').html('<span class="glyphicon glyphicon-map-marker" aria-hidden="true"></span> '+locationStr).appendTo($meta);
		
		
		// description
		markdown( this.$element.find('.info-description').text(this.device.description()));
		
		
		var toggleDescription = function(){
			
			var $description = self.$element.find('.info-description'),
				foldState = $description.data('fold');
			
			if(typeof foldState == 'undefined'){
				// init
				
				$description.data('fold', foldState = ($description.height() > descriptionMaxHeight));
				
				if(foldState){
					var $more = $('<button type="button" class="btn btn-link">More ...</button>').click(toggleDescription);
					$description.after($more);
				}
				
			}
			
			var maxHeight =  $description.css('max-height');
			
			if(maxHeight === 'none' || !maxHeight){
				// fold
				$description.css({
					'max-height': descriptionMaxHeight+'px',
					'overflow': 'hidden'
				});
				
				$description.next('button').text('more ...');
			}
			else {
				// expand
				$description.css({
					'max-height': '',
					'overflow': ''
				});
				$description.next('button').text('fold description');
			}
			
		};
		
		
		// widget
		if(this.device instanceof EThing.Device.MySensorsSensor){
			
			var sensorType = this.device.sensorType();
			
			require(['deviceWidget/'+sensorType.replace(/^S_/, '').toLowerCase()], function(WidgetClass){
				
				self.$element.find('.info').addClass('hasWidget');
				
				var $widget = self.$element.find('.info > div > .widget');
				$widget.data('widget', new WidgetClass($widget[0], self.device));
				
				
			}, function(){
				// default
			});
			
		}
		
		
		
		/*
		* API
		*/
		
		this.device.getApi().done(function(api){
			
			var device = this,
				operations = api,
				$api = self.$element.find('.api'),
				$apiContent = self.$element.find('.api>.content').empty();
			
			operations.forEach(function(operation){
				
				var name = operation.name,
					description = operation.description || '',
					schema = operation.schema;
				
				
				var $operation = $(
					'<div class="operation" id="'+name+'">'+
						'<div class="operation-header"></div>'+
						'<div class="operation-body">'+
							'<div class="operation-body-description"></div>'+
						'</div>'+
					'</div>'
				);
				
				$operation.data('operation', operation);
				
				$operation.find('.operation-header').text(name);
				
				// description
				markdown( $operation.find('.operation-body-description').text(description));
				
				
				var form = schema ? new $.Form.fromJsonSchema( schema ) : null;
				
				//console.log(form);
				
				if(name === 'sendMessage' && form && /^Device\\MySensors/.test(device.type())){
					// override default item, more convenient than dealing with number
					
					var typeOpt = $.extend({}, form.getLayoutItemByName('type'), {
						item: new $.Form.Select({
							items: MySensors_messageTypes
						})
					});
					form.replaceItemWith('type', typeOpt);
					
					var subtypeOpt = $.extend({}, form.getLayoutItemByName('subtype'), {
						item: new $.Form.Select({
							items: []
						}),
						dependencies: {
							'type': function(layoutItem){
								
								var type = this.getLayoutItemByName('type').item.value();
								
								switch(parseInt(type)){
									case 0:
										layoutItem.item.setOptions(MySensors_sensorTypes);
										break;
									case 1:
									case 2:
										layoutItem.item.setOptions(MySensors_valueTypes);
										break;
									case 3:
										layoutItem.item.setOptions(MySensors_internalTypes);
										break;
									case 4:
										layoutItem.item.setOptions(MySensors_streamTypes);
										break;
								}
								
							}
						}
					});
					form.replaceItemWith('subtype', subtypeOpt);
					
				}
				
				$operation.find('.operation-body').append(
					createView( 
						form,
						new OperationView(device, operation)
					)
				);
				
				
				$operation.find('.operation-body').hide();
				
				var toggle = function(state){
					state = typeof state == 'boolean' ? state : undefined;
					$operation.toggleClass('opened', state).find('.operation-body').slideToggle(state);
				};
				
				$operation.data('toggleFn', toggle);
				
				$operation.find('.operation-header').click(toggle);
				
				$apiContent.append($operation);
				
			}, this);
			
			/*if(operations.length == 1){
				// auto expand the first one
				$api.children('.operation').first().data('toggleFn')();
			}*/
			
			if($apiContent.children().length==0){
				$api.hide();
			}
			
		}).fail(function(){
			self.$element.find('.api').hide();
		});
		
		// only HTTP device has an api key
		if(this.device instanceof EThing.Device.Http)
			self.$element.find('.apikey').show();
		
		EThing.arbo.load(function(){
			
			var assocResources = EThing.arbo.find(function(r){
				return r.createdBy() && r.createdBy().id === self.device.id();
			});
			
			
			/*
			* DATA
			*/
			
			var tables = assocResources.filter(function(r){
				return r instanceof EThing.Table;
			});
			if(tables.length >= 1){
				
				var $data = self.$element.find('.data').show();
				
				
				require(['plot'], function(){
					
					$data.find('.content').empty().plot({
						sources: tables.map(function(table){
							return function(){
								return table.select({
									datefmt: 'TIMESTAMP_MS'
								});
							};
						})
					}, function(chart){
						setTimeout(function(){
							chart.reflow();
						},1);
					});
				});
			}
			
			
			
			
			/*
			* RESOURCE
			*/
			
			if(assocResources.length>0){
				
				require(['browser'], function(){
					self.$element.find('.resources').show().find('.content').browser({
						model: {
							root: assocResources
						},
						view:{
							header:{
								enable: true
							}
						},
						openable: {
							enable: true,
							open: function(r){
								UI.open(r);
							}
						}
					});
				});
			}
			
		});
		
		
		
	}
	
	return function(data){
		
		var $template = UI.Container.set('<div>loading ...</div>').addClass('container');
		
		var device = EThing.arbo.findOneById(data.rid);
		
		if(device){
			
			new DeviceViewer($template, {
				device: device
			});
			
		} else {
			UI.show404();
		}
		
	};
}));