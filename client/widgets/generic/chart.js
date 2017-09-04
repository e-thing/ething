(function (factory) {
	// AMD.
	define(['jquery','ething','form','resourceselect'], factory);
}(function ($, EThing, Form) {
	
	
	return {
		
		description: 'Draw a chart from data stored in your table !',
		
		// must return a function which returns an options object
		factory: function(container, preset){
			
			var form = new $.Form(container,new $.Form.FormLayout({
				items:[{
					name: 'title',
					item: new $.Form.Text()
				},{
					name: 'sources',
					item: new $.Form.ArrayLayout({
						editable: true,
						minItems: 1,
						value: [{}],
						instanciator: function(){
							return new $.Form.FormLayout({
								items:[{
									name: 'resource',
									label: 'table',
									item: new $.Form.ResourceSelect({
										filter: function(r){
											return r instanceof EThing.Table;
										},
										validators: [$.Form.validator.NotEmpty]
									})
								},{
									name: 'key',
									label: 'column',
									item: new $.Form.Text({
										validators: [$.Form.validator.NotEmpty],
										placeholder: 'Select the column'
									}),
									dependencies: {
										'resource': function(layoutItem){
											var r = EThing.arbo.findOneById(this.getLayoutItemByName('resource').item.value());
											layoutItem.item.setComboboxValues( r instanceof EThing.Table ? r.keys() : []);
											return r instanceof EThing.Table;
										}
									}
								},{
									name: 'range',
									item: new $.Form.Select({
										items: {
											'last 10 points': '10points',
											'last 100 points': '100points',
											'last hour': '3600sec',
											'last 6 hours': '21600sec',
											'last 12 hours': '43200sec',
											'last day': '86400sec',
											'last 2 days': '172800sec',
											'last week': '604800sec',
											'last month': '2678400sec',
											'all available data': '0',
										},
										value: '86400sec'
									})
								},{
									name: 'chartType',
									label: 'type of chart',
									item: new $.Form.Select({
										items: ['area','areaspline','column','line','scatter','spline'],
										value: 'line'
									})
								},{
									name: 'chartColor',
									label: 'chart color',
									item: new $.Form.Color({
										value: '#307bbb'
									})
								},{
									name: 'chartMarkerSize',
									label: 'chart marker size',
									item: new $.Form.Number({
										minimum: 0,
										maximum: 10,
										value: 4
									}),
									dependencies: {
										'chartType': function(layoutItem){
											return this.getLayoutItemByName('chartType').item.value() != 'column';
										}
									}
								}]
							});
						}
					})
				}]
			}), preset);
			
			return function(){
				return form.submit();
			}
		},
		
		require: ['widget/Widget','plot'],
		
		instanciate: function(options, Widget){
			
			
			var sources = [],
				resources = [];
			
			options.sources.forEach(function(source){
				
				var resource = EThing.arbo.findOneById(source.resource);
				var range = source.range || '0';
				var query = undefined, start = undefined;
				
				if(!resource)
					return new Error('The resource "'+source.resource+'"does not exist anymore');
				
				resources.push(resource);
				
				if(range && range != '0'){
					if(/^[0-9]+points$/.test(range)){
						// get last n values
						start = -parseInt(range);
					}
					else if(/^[0-9]+sec$/.test(range)){
						// date range
						var d = new Date( Date.now() - (parseInt(range)*1000) );
						query = "date > '"+d.toISOString()+"'";
					}
				}
				
				var name = source.key;
				if(resource.createdBy()){
					var createdByResource = EThing.arbo.findOneById(resource.createdBy().id);
					if(createdByResource)
						name = createdByResource.basename()+' - '+name;
				}
				
				sources.push( {data:function(){
					return resource.select({
						fields: ['date', source.key],
						datefmt: 'TIMESTAMP_MS',
						start: start,
						query: query
					}).then(function(data){
						return {
							data: data,
							name: name,
							color: source.chartColor || undefined,
							marker: {
								enabled: source.chartMarkerSize && source.chartMarkerSize>0,
								radius: source.chartMarkerSize
							},
							type: source.chartType || 'line'
						};
					});
				}});
				
			}, this);
			
			
			
			var widget = $.extend(Widget(), {
				
				draw: function(){
					
					this.$element.plot({
						sources: sources,
						explode: false,
						chart: {
							title: {
								text: options.title || null,
								style: {
									color: '#b3b3b3'
								},
								useHTML: true
							},
							rangeSelector: {
								enabled: false
							},
							plotOptions:{
								line: {
									marker: {
										enabled: true,
										radius: 4
									}
								}
							},
							yAxis: {
								tickPixelInterval: 50
							},
							scrollbar: {
								enabled: false
							},
							navigator: {
								enabled: false
							},
							chart: {
								zoomType: null,
								type: 'line'
							}
						}
					});
					
					resources.forEach(function(resource){
						resource.on('updated', update);
					});
					
				},
				
				resize: function(){
					var chart = this.$element.plot('chart');
					if(chart) chart.reflow();
				},
				
				destroy: function(){
					resources.forEach(function(resource){
						resource.off('updated', update);
					});
				}
				
			});
			
			
			var update = function(){
				widget.$element.plot('refresh');
			};
			
			
			return widget;
			
		}
	};
	
}));