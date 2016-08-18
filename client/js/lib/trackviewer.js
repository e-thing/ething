(function(){
	
	
	
	
	var addTrackFormHtml = '<div class="map-addTrack-form">'+
	  '<div class="form-group">'+
		'<label class="control-label">Table</label>'+
		'<select data-name="table" class="form-control">'+
		'</select>'+
	  '</div>'+
	  '<div class="form-group">'+
		'<label class="control-label">Longitude</label>'+
		'<select data-name="lon" class="form-control">'+
		'</select>'+
	  '</div>'+
	  '<div class="form-group">'+
		'<label class="control-label">Latitude</label>'+
		'<select data-name="lat" class="form-control">'+
		'</select>'+
	  '</div>'+
	  '<button class="btn btn-primary">Add</button>'+
	'</div>';
	
	
	
	
	
	function Track(element, opt){
		
		this.$element = $(element);
		
		var options = $.extend(true,{
			tracks: [], // [ [lat,lon] ... ], ...
			onload: null
		},opt);
		
		
		var self = this;
		
		this.$element.empty();
		
		
		this.options = function(){
			return options;
		}
		
		return EThing.utils.require([
			'//cdnjs.cloudflare.com/ajax/libs/ol3/3.15.1/ol.js','//cdnjs.cloudflare.com/ajax/libs/ol3/3.15.1/ol.css'
		]).done(function(){
			// ol loaded
			

			var vectorSource = self._vectorSource = new ol.source.Vector({});
			
			
			// tooltip
			var $tooltip = $('<div class="map-tooltip">').appendTo(self.$element);
			$tooltip.tooltip({
			  animation: false,
			  trigger: 'manual'
			});
			
			// addTrackForm
			var $addTrackForm = $(addTrackFormHtml).hide().appendTo(self.$element), tables = {};
			$addTrackForm.find('[data-name="table"]').change(function(){
				var tableId = $(this).val();
				
				var $lon = $addTrackForm.find('[data-name="lon"]').empty();
				var $lat = $addTrackForm.find('[data-name="lat"]').empty();
				
				if(tableId && tables.hasOwnProperty(tableId))
					tables[tableId].keys().forEach(function(key){
						$lon.append('<option '+(/lon/i.test(key) ? 'selected' : '')+'>'+key+'</option>');
						$lat.append('<option '+(/lat/i.test(key) ? 'selected' : '')+'>'+key+'</option>');
					});
			});
			$addTrackForm.find('button').click(function(){
				var tableId = $addTrackForm.find('[data-name="table"]').val();
				if(tableId && tables.hasOwnProperty(tableId)){
					var latField = $addTrackForm.find('[data-name="lat"]').val(),
						lonField = $addTrackForm.find('[data-name="lon"]').val();
					if(latField && lonField){
						tables[tableId].select({
							fields: [latField,lonField]
						}).done(function(data){
							var coordinates = [];
							data.forEach(function(point){
								if(point.hasOwnProperty(latField) && point.hasOwnProperty(lonField)){
									var lat = parseFloat(point[latField]), lon = parseFloat(point[lonField]);
									if(!isNaN(lat) && !isNaN(lon))
										coordinates.push([lon,lat]);
								}
							});
							self.addTrack({
								name: this.name(),
								coordinates: coordinates
							});
							$addTrackForm.hide();
							self.autoCenter();
						});
					}
				}
			});
			EThing.list('type == "Table"').done(function(resources){
				$table = $addTrackForm.find('[data-name="table"]');
				resources.forEach(function(table){
					if(table.keys().length){
						$table.append('<option value="'+table.id()+'">'+table.name()+'</option>');
						tables[table.id()] = table;
					}
				});
				$addTrackForm.find('[data-name="table"]').trigger('change');
			});
			
			
			// custom control
			var CenterControl = function(opt_options) {

				var options = opt_options || {};

				var button = document.createElement('button');
				button.innerHTML = '<span class="glyphicon glyphicon-screenshot" aria-hidden="true"></span>';

				var handleCenter = function() {
					self.autoCenter();
				};

				button.addEventListener('click', handleCenter, false);
				button.addEventListener('touchstart', handleCenter, false);

				var element = document.createElement('div');
				element.className = 'map-center-control ol-unselectable ol-control';
				element.appendChild(button);

				ol.control.Control.call(this, {
					element: element,
					target: options.target
				});

			};
			ol.inherits(CenterControl, ol.control.Control);
			var AddTrackControl = function(opt_options) {

				var options = opt_options || {};

				var button = document.createElement('button');
				button.innerHTML = '<span class="glyphicon glyphicon-plus" aria-hidden="true"></span>';

				var handleCenter = function() {
					
					$addTrackForm.toggle(100);
					
				};

				button.addEventListener('click', handleCenter, false);
				button.addEventListener('touchstart', handleCenter, false);

				var element = document.createElement('div');
				element.className = 'map-addTrack-control ol-unselectable ol-control';
				element.appendChild(button);

				ol.control.Control.call(this, {
					element: element,
					target: options.target
				});

			};
			ol.inherits(AddTrackControl, ol.control.Control);
			
			var map = new ol.Map({
				target: self.$element[0],
				layers: [
					// map
					/*new ol.layer.Tile({
						source: new ol.source.MapQuest({layer: 'osm'})
					}),*/
					new ol.layer.Tile({
						source: new ol.source.OSM()
					}),
					// features
					new ol.layer.Vector({
						source: vectorSource
					})
				],
				view: new ol.View({
					center: ol.proj.fromLonLat([1.443962, 43.604482]),
					zoom:5
				}),
				controls: ol.control.defaults().extend([
					new CenterControl(),
					new AddTrackControl()
				])
			});
			
			self.map = function(){
				return map;
			}
			
			if(Array.isArray(options.tracks)){
				for(var i=0; i<options.tracks.length; i++)
					self.addTrack(options.tracks[i]);
			}
			
			self.autoCenter();
			
			
			map.on('pointermove', function(e) {
			  if (e.dragging) {
				$tooltip.tooltip('hide');
				return;
			  }
			  
			  var feature = map.forEachFeatureAtPixel(e.pixel, function(feature, layer) {
				return feature;
			  });
			  
			  // change mouse cursor when over marker
			  // map.getTarget().style.cursor = feature ? 'pointer' : '';
			  
			  // tooltip
			  if (feature) {
				var geometry = feature.getGeometry(),
					coordinates = (geometry instanceof ol.geom.Point) ? geometry.getCoordinates() : e.coordinate,
					pixel = map.getPixelFromCoordinate(coordinates);
				
				$tooltip
					.tooltip('hide')
					.css({
						left: pixel[0] + 'px',
						top: (pixel[1] - 5) + 'px'
					  })
					.attr('data-original-title', feature.get('name'))
					.tooltip('fixTitle')
					.tooltip('show');
			  } else {
				$tooltip.tooltip('hide');
			  }
			  
			});
			
			map.on('click', function(e) {
				$addTrackForm.hide(100);
			});
			
			if(typeof options.onload == 'function')
				self.map().once('postrender',options.onload,self);
			
		});
		
	}
	
	Track.prototype.autoCenter = function(){
		
		var map = this.map(),
			source = this._vectorSource,
			length = source.getFeatures().length;
		
		if(length)
			map.getView().fit(source.getExtent(), map.getSize(), {
				maxZoom: length>1 ? 19 : 15
			});
		
	}
	
	Track.prototype.addTrack = function(opt){
		
		var src = this._vectorSource;
		
		if(ol && src){
			
			if(Array.isArray(opt))
				opt = {
					coordinates: opt
				};
			
			var options = $.extend(true,{
				coordinates: [],
				name: null
			},opt);
			
			
			var c = [];
			for(var i=0; i<options.coordinates.length; i++)
				c.push(ol.proj.fromLonLat(options.coordinates[i]));
			
			if(c.length==0) return;
			
			if(!options.name)
				options.name = 'track '+ (src.getFeatures().length + 1);
			
			var feature = new ol.Feature({
				geometry: new ol.geom.LineString(c),
				name: options.name
			});
			
			feature.setStyle([
				new ol.style.Style({
				  stroke: new ol.style.Stroke({
					color: 'rgba(0, 0, 255, 0.7)',
					width: 1
				  })
				}),
				new ol.style.Style({
				  image: new ol.style.Circle({
					radius: 2,
					fill: new ol.style.Fill({
					  color: 'rgba(0, 0, 255, 0.5)'
					})
				  }),
				  geometry: function(feature) {
					var coordinates = feature.getGeometry().getCoordinates();
					return new ol.geom.MultiPoint(coordinates);
				  }
				})
			]);
			
			src.addFeature(feature);
			
		}
		
		
	}
	
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery)
		window.jQuery.addPlugin('Track',Track);
	
	
})();