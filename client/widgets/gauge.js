(function(){
	
	
	var gaugeOptions = {

        chart: {
            type: 'solidgauge'
        },

        title: null,

        pane: {
            center: ['50%', '85%'],
            size: '140%',
            startAngle: -90,
            endAngle: 90,
            background: {
                backgroundColor: '#EEE',
                innerRadius: '60%',
                outerRadius: '100%',
                shape: 'arc'
            }
        },

        tooltip: {
            enabled: false
        },

        // the value axis
        yAxis: {
            stops: [
                [0.1, '#55BF3B'], // green
                [0.5, '#DDDF0D'], // yellow
                [0.9, '#DF5353'] // red
            ],
            lineWidth: 0,
            minorTickInterval: null,
            tickPixelInterval: 400,
            tickWidth: 0,
            title: {
                y: -70
            },
            labels: {
                y: 16
            }
        },

        plotOptions: {
            solidgauge: {
                dataLabels: {
                    y: 5,
                    borderWidth: 0,
                    useHTML: true
                }
            }
        },
		
		credits: {
            enabled: false
        },
		
		exporting: {
			enabled: false
		}
    };
	
	
	
	var Gauge = function(element,options){
		
		
		var css = {
			
		};
		
		var $element = $(element);
		
		$element.css(css);
		
		EThing.Table.select(options.value.tableId, {
			fields: [options.value.field],
			start: -1,
			length: 1
		}).done(function(data){
			if(data.length && data[0].hasOwnProperty(options.value.field)){
				var value = data[0][options.value.field];
				
				// The RPM gauge
				$element.highcharts(Highcharts.merge(gaugeOptions, {
					
					title: {
						text: options.value.field
					},
					
					yAxis: {
						min: options.minimum,
						max: options.maximum,
						title: null
					},

					series: [{
						name: options.value.field,
						data: [value],
						dataLabels: {
							format: '<div style="text-align:center"><span style="font-size:25px;color:' +
								((Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black') + '">{y:.1f}</span><br/>' +
								   '</div>'
						}
					}]

				}));
			}
		});
		
	}
	
	
	
	return {
		// must return a function which returns an options object
		factory: function(container, preset){
			var form = new $.Form(container,{
				'value': new $.Form.TableFieldSelect(),
				'minimum':'number',
				'maximum':'number'
			});
			
			if(preset)
				form.setValue(preset);
			
			return function(){
				return form.validate();
			}
		},
		
		instanciate: function(element, options){
			new Gauge(element,options);
		},
		
		require: {
			url: '//code.highcharts.com/stock/highstock.js',
			then: [{
				url: '//code.highcharts.com/stock/highcharts-more.js',
				then: '//code.highcharts.com/stock/modules/solid-gauge.js'
			},'//code.highcharts.com/stock/modules/exporting.js']
		}
	};
	
})()