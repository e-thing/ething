(function(){
	
	var dependency = $.Dependency({
		url: ['//cdnjs.cloudflare.com/ajax/libs/ol3/3.15.1/ol.js','//cdnjs.cloudflare.com/ajax/libs/ol3/3.15.1/ol.css']/*,
		then: '//cdn.rawgit.com/walkermatt/ol3-layerswitcher/master/src/ol3-layerswitcher.js'*/
	},function(){
		// custom control
		ol.control.CustomControl = function(opt_options) {

			var options = opt_options || {
				glyphicon: null,
				click: null,
				class: null
			};

			var button = document.createElement('button');
			button.innerHTML = '<span class="glyphicon glyphicon-'+options.glyphicon+'" aria-hidden="true"></span>';

			button.addEventListener('click', options.click, false);
			button.addEventListener('touchstart', options.click, false);

			var el = document.createElement('div');
			el.className = options.class + ' ol-unselectable ol-control';
			el.appendChild(button);

			ol.control.Control.call(this, {
				element: el,
				target: options.target
			});

		};
		ol.inherits(ol.control.CustomControl, ol.control.Control);
	});
	

	
	
	
	
	function getResourceLocation(resource){
		return (typeof resource.location == 'function' && resource.location()) ? resource.location() : null;
	}
	
	
	function MapViewer(element,options){
		var self = this;
		
		$.AbstractPlugin.call(this,element,$.extend(true,{
			marker:{
				onClick: null // function(resource) fired when a marker is clicked
			},
			center: null, // can either be google.maps.LatLng, or a resource
			onload: null,
			resources: []
		},options));
		
		
		this.$element.empty().addClass('mapviewer');
		
		
		function init(){
			
			var center = this.options.center,
				autocenter = false;
			
			if(Array.isArray(center) && center.length == 2){
				center = ol.proj.fromLonLat(center);
			}
			else if(center instanceof EThing.Resource){
				var loc = getResourceLocation(center);
				center = ol.proj.fromLonLat([loc.longitude, loc.latitude]);
			}
			else {
				autocenter = true;
				center = null;
			}
			
			
			// feature layer
			this._featuresLayer = new ol.layer.Vector({
				source: new ol.source.Vector({})
			});
			
			var _map = new ol.Map({
				target: this.$element[0],
				layers: [
					// maps
					new ol.layer.Tile({
						title: 'Map',
						type: 'base',
                        visible: true,
						source: new ol.source.OSM()
					}),
					/*new ol.layer.Tile({
                        title: 'Satellite',
                        type: 'base',
                        visible: false,
                        source: new ol.source.MapQuest({layer: 'sat'}) // need an api key since 11 july 2016
                    }),*/
					// features
					this._featuresLayer
				],
				view: new ol.View({
					center: center || ol.proj.fromLonLat([1.443962, 43.604482]),
					zoom:5
				}),
				controls: ol.control.defaults().extend([
					new ol.control.CustomControl({
						click: function(){
							self.autoCenter();
						},
						class: 'map-center-control',
						glyphicon: 'screenshot'
					})/*, new ol.control.LayerSwitcher()*/
				])
			});
			
			this.map = function(){
				return _map;
			}
			
			
			// tooltip
			var $tooltip = $('<div class="map-tooltip">').appendTo(this.$element);
			$tooltip.tooltip({
			  animation: false,
			  trigger: 'manual'
			});
			
			// setup popup overlay
			var $popup = $('<div>').appendTo(this.$element);
			this._popup = new ol.Overlay({
			  id: "popup",
			  element: $popup[0],
			  positioning: 'bottom-center',
			  stopEvent: false,
			  autoPan: true,
			  autoPanAnimation: {
			    duration: 250
			  }
			});
			_map.addOverlay(this._popup);
			
			
			// events
			_map.on('click', function(e) {
			  var feature = _map.forEachFeatureAtPixel(e.pixel,
				  function(feature, layer) {
					return feature;
				  });
			  if (feature) {
				var resource = feature.get('resource');
				
				self.showPopup(resource);
				
				if(typeof self.options.marker.onClick == 'function')
					self.options.marker.onClick.call(self,resource);
				
			  } else {
				self.hidePopup();
			  }
			});

			
			if(!EThing.utils.isTouchDevice) _map.on('pointermove', function(e) {
			  if (e.dragging) {
				$tooltip.tooltip('hide');
				return;
			  }
			  
			  var feature = _map.forEachFeatureAtPixel(e.pixel, function(feature, layer) {
				return feature;
			  });
			  
			  // change mouse cursor when over marker
			  _map.getTarget().style.cursor = feature ? 'pointer' : '';
			  
			  // tooltip
			  if (feature && $popup.data('f') !== feature) {
				var geometry = feature.getGeometry(),
					coordinates = (geometry instanceof ol.geom.Point) ? geometry.getCoordinates() : e.coordinate,
					pixel = _map.getPixelFromCoordinate(coordinates);
				
				$tooltip
					.tooltip('hide')
					.css({
						left: pixel[0] + 'px',
						top: (pixel[1] - 35) + 'px'
					  })
					.attr('data-original-title', feature.get('name'))
					.tooltip('fixTitle')
					.tooltip('show');
			  } else {
				$tooltip.tooltip('hide');
			  }
			  
			});
			
			
		
			if(this.add(this.options.resources)){
				if(autocenter)
					this.autoCenter();
			}
			else {
				// no resource to draw
				this.$element.prepend('<div class="alert alert-warning map-alert" role="alert">No resource to show !</div>');
			};
			
			if(typeof this.options.onload == 'function')
				this.map().once('postrender',this.options.onload,this);
		}
		
		dependency.require(function(){
			init.call(self);
		});
		
	}
	
	MapViewer.prototype.autoCenter = function(){
		
		var map = this.map(),
			source = this._featuresLayer.getSource(),
			length = source.getFeatures().length;
		
		if(length)
			map.getView().fit(source.getExtent(), map.getSize(), {
				maxZoom: length>1 ? 19 : 15
			});
		
	}
	
	MapViewer.prototype.add = function(resources, cb){
		var added = 0;
		
		if(!Array.isArray(resources))
			resources = (resources===null || typeof resources == 'undefined') ? [] : [resources];
		
		resources.forEach(function(resource){
			
			// check if this resource has a loaction attribute set
			var loc = getResourceLocation(resource);
			
			if(loc){
				
				
				var color;
			
				switch(resource.type()){
					case 'Device':
						color = "9b59b6";
						break;
					case 'File':
						color = "1abc9c";
						break;
					case 'Table':
						color = "3498db";
						break;
					case 'App':
						color = "2ecc71";
						break;
					default:
						color = "CC2EAD";
						break;
				}
				
				var map = this.map(),
					vectorSource = this._featuresLayer.getSource(),
					icon = "//chart.googleapis.com/chart?chst=d_map_pin_letter&chld="+resource.type()[0]+"|" + color,
					coordinates = ol.proj.fromLonLat([loc.longitude,loc.latitude]);
				
				
				var iconStyle = new ol.style.Style({
				  image: new ol.style.Icon({
					anchor: [0.5, 1],
					anchorXUnits: 'fraction',
					anchorYUnits: 'fraction',
					opacity: 0.75,
					src: icon
				  })
				});
				//create icon at new map center
				var iconFeature = new ol.Feature({
					geometry: new ol.geom.Point(coordinates),
					name: resource.name(),
					resource: resource
				});
				
				iconFeature.setStyle(iconStyle);

				//add icon to vector source
				vectorSource.addFeature(iconFeature);
				added++;
				
			}
			
		},this);
		
		return added;
	}
	
	
	MapViewer.prototype.showPopup = function(resource){
		if(!resource) 
			return;
		var feature = this._feature(resource),
			popup = this._popup,
			map = this.map();
		if(!feature || !popup) 
			return;
		
		// calculate the center of the geometry !
		var extent = feature.getGeometry().getExtent(),
			coordinates = [ (extent[0] + extent[2])/2 , (extent[1] + extent[3])/2 ];
		
		var popupGenerateContent = function(resource){
			var loc = resource.location(),
				content = '<div class="map-popup-content">';
			
			content += '<h4>'+resource.name()+' <small>['+resource.type()+']</small></h4>';
			
			// print location
			content += '<p><span class="glyphicon glyphicon-map-marker" aria-hidden="true"></span> '+loc.latitude+"N "+loc.longitude+"E"+'</p>';
			
			// print date
			var date = (resource instanceof EThing.Device) ? resource.lastSeenDate() : resource.modifiedDate();
			content += '<p><span class="glyphicon glyphicon-time" aria-hidden="true"></span> '+(date ? EThing.utils.dateDiffToString( Math.floor( (Date.now() - date.getTime()) / 1000 ) ) : 'never')+'</p>';
			
			// print description if any
			var description = resource.description();
			if( description && description.length)
				content += '<p>'+description+'</p>';
			
			content += '</div>';
			
			return content;
		}
		
		// popup
		popup.setPosition(coordinates);
		$(popup.getElement())
			.data('f',feature)
			.popover({
			  'trigger': 'manual',
			  'placement': 'top',
			  'html': true,
			  'template': '<div class="popover map-popup" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>',
			  'content': function(){
				return popupGenerateContent.call(map,$(this).data('f').get('resource'));
			  }
			})
			.popover('show');
		
	}
	
	MapViewer.prototype.hidePopup = function(){
		var $popup = $(this._popup.getElement());
		$popup.popover('destroy');
		$popup.data('f',null);
	}
	
	MapViewer.prototype._feature = function(resource){
		// return the feature of a resource
		var features = this._featuresLayer.getSource().getFeatures();
		for(var i=0; i<features.length; i++){
			if(features[i].get('resource').id() == resource.id())
				return features[i];
		}
	}
	
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery)
		window.jQuery.addPlugin('MapViewer',MapViewer);
	
	
})();