(function(){
		
	
	return {
		
		description: 'Draw a chart from data stored in your table !',
		
		// must return a function which returns an options object
		factory: function(container, preset){
			var form = new $.Form(container,{
				'value': new $.Form.TableFieldSelect(),
				'range': new $.Form.Select({
					items: {
						'10 points': '10p',
						'100 points': '100p',
						'1 hour': 3600,
						'6 hours': 21600,
						'12 hours': 43200,
						'1 day': 86400,
						'2 days': 172800,
						'1 week': 604800,
						'1 month': 2678400,
						'all': 0,
					},
					value: 86400
				}),
				'unit': 'text'
			});
			
			if(preset)
				form.setValue(preset);
			
			return function(){
				return form.validate();
			}
		},
		
		instanciate: function(element, options){
			return EThing.get(options.value.tableId).done(function(table){
				
				var length = 0,
					query = '',
					unit = (options.unit || '').trim();
				
				if(options.range && options.range != '0'){
					if(/^[0-9]+p$/.test(options.range)){
						// get last n values
						length = parseInt(options.range);
					}
					else if(/^[0-9]+$/.test(options.range)){
						// date range
						var d = new Date( Date.now() - (parseInt(options.range)*1000) );
						query = "date > '"+d.toISOString()+"'";
					}
				}
				
				var hcopt = $.extend(true,$.Graph.defaultOptionsFromTable(table, options.value.field, length, query),{
					highstock: false,
					navigator : {
						enabled : false
					},
					rangeSelector: {
						enabled: false
					},
					exporting: {
						enabled: false
					},
					legend: {
						enabled: false
					},
					xAxis: {
						tickPixelInterval: 80,
						title: null
					},
					title:{
						text: options.value.field
					}
				});
				
				// set y axis title
				for(var i=0; i<hcopt.yAxis.length; i++)
					hcopt.yAxis[i].title = unit ? { text: unit } : null;
				
				new $.Graph(element,hcopt);
			});
		}
	};
	
})()