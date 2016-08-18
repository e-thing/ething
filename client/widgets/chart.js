(function(){
		
	
	return {
		// must return a function which returns an options object
		factory: function(container, preset){
			var form = new $.Form(container,{
				'value': new $.Form.TableFieldSelect()
			});
			
			if(preset)
				form.setValue(preset);
			
			return function(){
				return form.validate();
			}
		},
		
		instanciate: function(element, options){
			EThing.get(options.value.tableId).done(function(table){
				
				var hcopt = $.extend(true,$.Graph.defaultOptionsFromTable(table, options.value.field, 100),{
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
				
				// remove y axis title
				for(var i=0; i<hcopt.yAxis.length; i++)
					hcopt.yAxis[i].title = null;
				
				new $.Graph(element,hcopt);
			});
		}
	};
	
})()