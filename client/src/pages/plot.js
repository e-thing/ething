(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ui/core', 'jquery', 'ething', 'ui/infopanel', 'plot', 'ui/formmodal', 'ui/tablefieldselect', 'ui/savedialog'], factory);
    }
}(this, function (UI, $, EThing, Infopanel) {
	
	// Cf: https://stackoverflow.com/questions/8572826/generic-deep-diff-between-two-objects
	var deepDiffMapper = function() {
		return {
			VALUE_CREATED: 'created',
			VALUE_UPDATED: 'updated',
			VALUE_DELETED: 'deleted',
			VALUE_UNCHANGED: 'unchanged',
			map: function(obj1, obj2, diffs, path) {
				
				path = path || '';
				
				if (this.isFunction(obj1) || this.isFunction(obj2)) {
					throw 'Invalid argument. Function given, object expected.';
				}
				if (this.isValue(obj1) || this.isValue(obj2)) {
					var d = {
						path: path,
						type: this.compareValues(obj1, obj2),
						data: (obj1 === undefined) ? obj2 : obj1
					};
					if(typeof diffs === 'object' && diffs !== null && d.type!=this.VALUE_UNCHANGED) diffs[path] = d;
					return d;
				}
				
				if(path!=='') path = path+'.';

				var diff = {};
				for (var key in obj1) {
					if (this.isFunction(obj1[key])) {
						continue;
					}

					var value2 = undefined;
					if ('undefined' != typeof(obj2[key])) {
						value2 = obj2[key];
					}

					diff[key] = this.map(obj1[key], value2, diffs, path+key);
				}
				for (var key in obj2) {
					if (this.isFunction(obj2[key]) || ('undefined' != typeof(diff[key]))) {
						continue;
					}

					diff[key] = this.map(undefined, obj2[key], diffs, path+key);
				}

				return diff;

			},
			compareValues: function(value1, value2) {
				if (value1 === value2) {
					return this.VALUE_UNCHANGED;
				}
				if (this.isDate(value1) && this.isDate(value2) && value1.getTime() === value2.getTime()) {
					return this.VALUE_UNCHANGED;
				}
				if ('undefined' == typeof(value1)) {
					return this.VALUE_CREATED;
				}
				if ('undefined' == typeof(value2)) {
					return this.VALUE_DELETED;
				}

				return this.VALUE_UPDATED;
			},
			isFunction: function(obj) {
				return {}.toString.apply(obj) === '[object Function]';
			},
			isArray: function(obj) {
				return {}.toString.apply(obj) === '[object Array]';
			},
			isDate: function(obj) {
				return {}.toString.apply(obj) === '[object Date]';
			},
			isObject: function(obj) {
				return {}.toString.apply(obj) === '[object Object]';
			},
			isValue: function(obj) {
				return !this.isObject(obj) && !this.isArray(obj);
			}
		}
	}();
	
	
	
	
	function createPreferencesPage(preset, callback, cancellable){
		
		
		var preferencesForm = new $.Form.FormLayout({
			items: [{
				name: 'title',
				item: new $.Form.Text()
			},{
				name: 'subtitle',
				item: new $.Form.Text()
			},{
				name: 'panes',
				description: 'At least 1 pane must be set.',
				item: new $.Form.ArrayLayout({
					editable: true,
					minItems: 1,
					instanciator: function(){
						
						var paneForm = new $.Form.FormLayout({
							items: [{
								name: 'title',
								label: 'name/unit',
								item: new $.Form.Text()
							},{
								name: 'curves',
								description: 'At least 1 curve must be set.',
								item: new $.Form.ArrayLayout({
									editable: true,
									minItems: 1,
									instanciator: function(){
										
										var curveForm = new $.Form.FormLayout({
											items: [{
												name: 'data',
												item: new $.Form.TableFieldSelect({
													validators:[$.Form.validator.NotEmpty]
												})
											},{
												name: 'filter',
												item: new $.Form.Text({
													placeholder: 'date > "12 hours ago"'
												})
											},{
												name: 'name',
												item: new $.Form.Text({
													validators:[$.Form.validator.NotEmpty]
												})
											},{
												name: 'type',
												item: new $.Form.Select(['line','column','scatter','area','spline'])
											},{
												name: 'color',
												item: new $.Form.Color({
													validators:[$.Form.validator.NotEmpty]
												})
											}]
										});
										
										return curveForm;
									}
								})
							}]
						});
						
						return paneForm;
					}
				})
				
			}]
		});
		
		
		$.FormModal({
			title: 'Graph properties',
			item: preferencesForm,
			value: preset,
			cancellable: !!cancellable
		}, callback);
		
	}
	
	
	
	function createPlot($element, preferences){
		
		var menu = {
			'properties': function(){
				updatePlot($element);
			},
			'save': function(){
				
				$.SaveDialog({
					filter: function(r){
						return r instanceof EThing.File && r.extension() === 'plot';
					},
					title: 'Save plot',
					preset: $element.data('file'),
					createPreset: {
						name: 'myplot.plot',
						type: 'File'
					},
					done: function(r){
						return r.write( JSON.stringify($element.data('preferences'), null, ' ') ).done(function(){
							$element.data('file', r);
							UI.setUrl('plot',{
								rid: r.id()
							});
						});
					},
					createTypes: ['File']
				});
				
			}
		};
		
		
		
		var plotOptions = {
			sources: [],
			chart: {
				title: {
					text: preferences.title || null
				},
				subtitle: {
					text: preferences.subtitle || null
				},
				yAxis: []
			},
			menu: menu
		};
		
		preferences.panes.forEach(function(pane, paneIndex){
			
			plotOptions.chart.yAxis.push({
				title: {
					text: pane.title || null
				}
			});
			
			pane.curves.forEach(function(curve, curveIndex){
				
				var table = EThing.arbo.findOneById(curve.data.table);
				
				plotOptions.sources.push({
					data: function(){
						return table.select({
							fields: ['date', curve.data.field],
							datefmt: 'TIMESTAMP_MS',
							query: curve.filter || null
						});
					},
					pane: paneIndex,
					serie: {
						color: curve.color,
						name: curve.name,
						type: curve.type
					}
				});
				
			});
			
		});
		
		$element.data('preferences', preferences);
		$element.plot(plotOptions);
		
	}
	
	
	function updatePlot($element){
		
		var preferences = $element.data('preferences');
		if(!preferences) return;
		
		createPreferencesPage(preferences, function(newPreferences){
			
			$element.data('preferences', newPreferences);
			
			var diffs = {};
			var result = deepDiffMapper.map(newPreferences, preferences, diffs);
			
			var diffkeys = Object.keys(diffs);
			if(diffkeys.length===0){
				return; // no changes
			} else {
				
				var updateFn = [{
					re: /^title$/,
					fn: function(chart, key, preferences){
						chart.update({
							title:{
								text: preferences.title || null
							}
						}, false);
					}
				},{
					re: /^subtitle$/,
					fn: function(chart, key, preferences){
						chart.update({
							subtitle:{
								text: preferences.subtitle || null
							}
						}, false);
					}
				}];
				
				var fullReload = false;
				var updateFns = [];
				
				diffkeys.forEach(function(key){
					
					var match = false;
					
					updateFn.forEach(function(updateRule){
						if(updateRule.re.test(key)){
							updateFns.push({
								key: key,
								fn: updateRule.fn
							});
							match = true;
							return false;
						}
					});
					
					if(!match){
						fullReload = true;
						return false;
					}
				});
				
				if(fullReload) {
					createPlot($element, newPreferences);
				} else {
					
					var chart = $element.plot('chart');
					updateFns.forEach(function(o){
						o.fn(chart, o.key, newPreferences);
					});
					chart.redraw();
				}
				
			}
			
		}, true);
		
		
	}
	
	return {
		
		buildView: function(data){
			
			var resource = data.rid ? this.resource = EThing.arbo.findOneById(data.rid) : null;
			var $element = UI.Container.set('<div class="ui-container-absolute">');
			
			var start = function(){
				createPreferencesPage(null, function(preferences){
					createPlot($element, preferences);
				});
			};
			
			if(resource && resource instanceof EThing.Table){
				
				if(data.fields && typeof data.fields === 'string')
					data.fields = data.fields.split(',');
				
				data.fields = data.fields || resource.keys();
				
				if(data.fields.indexOf('date')===-1)
					data.fields.push('date');
				
				UI.Header.setTitle(resource.basename());
				
				Infopanel.enable();
				Infopanel.setResource(resource);
				
				$element.plot({
					data: function(){
						return resource.select({
							fields: data.fields,
							datefmt: 'TIMESTAMP_MS'
						});
					},
					explode: true
				});
				
				this.update = function(){
					$element.plot('refresh');
				};
				
				resource.on('updated', this.update);
				
				
			} else if(resource && resource instanceof EThing.File) {
				// load from file !
				
				function error(){
					UI.setUrl('plot',{});
					start();
				};
				
				resource.read().done(function(preferences){
					
					if(typeof preferences == 'string'){
						try {
							preferences = JSON.parse(preferences);
						} catch(e){
							console.error(e);
							error();
						}
					}
					
					$element.data('file', resource);
					createPlot($element, preferences);
					
				}).fail(error);
				
			} else {
				
				start()
				
			}
		},
		
		deleteView: function(){
			
			if(this.resource){
				this.resource.off('updated', this.update);
			}
		}
		
	};
}));