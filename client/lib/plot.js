(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define([
			'jquery',
			'highstock',
			'highcharts/plugin/highcharts-data-deferred'
			], factory);
    } else {
        // Browser globals
        root.Plot = factory(root.jQuery, root.Highcharts);
    }
}(this, function ($, Highcharts) {
	
	
	Highcharts.setOptions({
		global: {
			useUTC: false
		}
	});
	
	var defaultChartOptions = {
		chart: {
			plotBorderWidth: 1,
			zoomType: 'x'
		},
		rangeSelector: {
			buttons: [{
				type: 'hour',
				count: 12,
				text: '12h'
			},{
				type: 'day',
				count: 1,
				text: '1d'
			},{
				type: 'week',
				count: 1,
				text: '1w'
			},{
				type: 'month',
				count: 1,
				text: '1m'
			}, {
				type: 'all',
				text: 'All'
			}],
			selected: 1
		},
		tooltip: {
			xDateFormat: '%Y-%m-%d %H:%M'
		},
		responsive: {
            rules: [{
                condition: {
                    maxHeight: 400
                },
                chartOptions: {
                    navigator: {
                        enabled: false
                    }
                }
            }]
        },
		xAxis: {
			ordinal: false,
			tickLength: 5
		},
		credits: {
			enabled: false
		}
	};
	
	var defaultSerieOptions = {
		showInNavigator: true
	};
	
	
	function Plot(element, options, onload, onfail){
		
		var self = this;
		
		this.$element = $(element).addClass('plot');
		this.options = $.extend(true, {
			sources: [], // source of data ... array of EThing.Table|function|Deferred|array|object|HighChart serie object
			data : null, // EThing.Table|function|array :the data to plot, if a function is given, the function must return the data.
			chart: null, // highcharts options
			explode: true // each serie in a single pane
		}, options);
		
		
		this.$element.html('<h6 style="color:grey;text-align: center;">loading ...</h6>');
		
		
		if( this.options.data ){
			this.options.sources.push(this.options.data);
		}
		
		// loads the data
		this.draw().done(onload).fail(onfail);
		
		
		
	}
	
	Plot.prototype.draw = function(){
		var self = this;
		
		if(this.chart){
			this.chart.destroy();
			this.chart = null;
		}
		
		
		var exportingMenuItems = Highcharts.defaultOptions.exporting.buttons.contextButton.menuItems.slice();
		exportingMenuItems.splice(0,1,{
			text: "update",
			onclick: function(){
				self.refresh();
			}
		});
		
		var chartOptions = $.extend(true, {
			exporting:{
				buttons:{
					contextButton:{
						menuItems: exportingMenuItems
					}
				}
			}
		}, defaultChartOptions, this.options.chart || {});
		
		var dfr = $.Deferred();
		
		this.getSeriesFromSources().done(function(series){
			
			/*if(!series || !series.length){
				dfr.rejectWith(self,[new Error('nothing to draw')]);
				return;
			}*/
			
			var optSeries = chartOptions.series || [];
			series.forEach(function(serie){
				
				// find if there is some user options for that serie
				optSeries.forEach(function(userSerie){
					if(serie.name===userSerie.name){
						$.extend(true, serie, userSerie);
					}
				});
				
			});
			
			
			for(var i =0; i<series.length; i++)
				series[i] = $.extend(true, {}, defaultSerieOptions, series[i]);
			
			chartOptions.series = series;
			
			var defaultYaxisOptions = {
				labels: {
					align: 'right',
					x: -3,
					y: 4
				},
				lineWidth: 1,
				opposite: false,
				showLastLabel: true,
				gridLineWidth: 1
			};
			
			var defaultYaxis = $.isPlainObject(chartOptions.yAxis) ? chartOptions.yAxis : {};
			
			// each serie on a different pane
			if(chartOptions.series.length>1 && self.options.explode){
				var marge = 5; // vertical space between 2 panes (in %)
				
				var yAxis = [];
				
				var seriesLength = chartOptions.series.length;
				var paneHeight = (100-(seriesLength-1)*marge)/seriesLength; // in %
				
				chartOptions.series.forEach(function(serie, index){
					
					var yOpt = $.extend({}, defaultYaxisOptions, defaultYaxis);
					
					yOpt.title = yOpt.title || {};
					yOpt.title.text = serie.name;
					
					yOpt.height = paneHeight+'%';
					yOpt.top = (index*(paneHeight+marge))+'%';
					yOpt.offset = 0;
					
					serie.yAxis = index;
					
					yAxis.push(yOpt);
					
				});
				
				chartOptions.yAxis = yAxis;
			} else {
				chartOptions.yAxis = $.extend({}, defaultYaxisOptions, defaultYaxis)
			}
			
			
			//console.log($.extend(true,{},chartOptions));
			
			self.$element.empty().highcharts('StockChart', chartOptions, function(chart){
				
				self.chart = chart;
				
				dfr.resolveWith(self,[chart]);
				
				if(chart.series.length===0)
					chart.showLoading('no data');
				
			});
			
			
		}).fail(function(err){
			console.error(err);
			var m = 'error';
			if(typeof err === 'string' || err instanceof Error)
				m += ': '+String(err);
			self.$element.empty().html('<h6 style="color:#d9534f;text-align: center;">'+m+'</h6>');
			dfr.rejectWith(self,[err]);
		});
		
		return dfr.promise();
	};
		
	// reload the data
	Plot.prototype.refresh = function(sourceIndex){
		var self = this;
		
		self.chart.showLoading('loading ...');
		
		this.getSeriesFromSources(sourceIndex).done(function(series){
			
			series.forEach(function(serie){
				
				var found = false;
				self.chart.series.forEach(function(chartSerie){
					if(chartSerie.name === serie.name){
						found = true;
						// update it !
						chartSerie.setData(serie.data, true, false, false);
						return false;
					}
				});
				
				if(!found){
					// create the serie : todo
				}
				
			});
			
			self.chart.hideLoading();
			
		}).fail(function(err){
			var m = 'error';
			if(typeof err === 'string' || err instanceof Error)
				m += ': '+String(err);
			self.chart.showLoading(m); // todo: remove this message after a while ... ?
			console.error(err);
		});
		
		
	}
	
	Plot.prototype.getSeriesFromSources = function(sourceIndex){
		var self = this;
		var dfrs = [];
		var dfr = $.Deferred();
		var sources = Array.isArray(this.options.sources) ? this.options.sources : [this.options.sources];
		
		sources.forEach(function(src, index){
			
			if(
				typeof sourceIndex === 'undefined' || sourceIndex===null ||
				(typeof sourceIndex === 'number' && index === sourceIndex) ||
				(Array.isArray(sourceIndex) && sourceIndex.indexOf(sourceIndex) !== -1)
			) {
				
				dfrs.push( this.getSeriesFromSource(src) );
				
			} else {
				dfrs.push( null );
			}
			
		}, this);
		
		$.when.apply($, dfrs).done(function(){
			
			var series = [];
			
			Array.prototype.slice.call(arguments).forEach(function(srcSeries){
				series = series.concat(srcSeries);
			});
			
			dfr.resolveWith(self, [series]);
			
		}).fail(function(e){
			dfr.rejectWith(self, [e]);
		});
		
		return dfr.promise();
	};
	
	Plot.prototype.getSeriesFromSource = function(source){
		
		if(typeof source === 'function'){
			return this.getSeriesFromSource(source.apply(this));
		} else if(source instanceof EThing.Table){
			return this.getSeriesFromSource(source.select({
				datefmt: 'TIMESTAMP_MS'
			}).then(function(data){
				return data;
			}) );
		} else {
			
			var dfr = $.Deferred(),
			self = this;
			
			$.when(source).done(function(data){
				try {
					var series = [].concat(DataReader.parse(data));
					dfr.resolveWith(self, [series]);
				} catch(err){
					dfr.rejectWith(self, [err]);
				}
				
			}).fail(function(err){
				dfr.rejectWith(self, [err]);
			});
			
			return dfr.promise();
		}
	};
	
	var DataReader = {
		
		parse: function(data){
			
			
			if(Array.isArray(data)){
				
				if(data.length===0)
					return [];
				
				var data0 = data[0];
				
				if(Array.isArray(data0)){
					return DataReader.fromDataArray(data);
				} else if($.isPlainObject(data0)){
				
					if(data0.hasOwnProperty('x')){
						return DataReader.fromDataArray(data);
					} else if(data0.hasOwnProperty('name') && data0.hasOwnProperty('data')){
						return DataReader.fromSerieArray(data);
					} else {
						return DataReader.fromDataArrayObj(data);
					}
					
				} else {
					console.log(data);
					throw 'invalid data';
				}
				
			} else if($.isPlainObject(data)){
				
				if(data.hasOwnProperty('name') && data.hasOwnProperty('data')){
					return DataReader.fromSerieObj(data);
				} else {
					return DataReader.fromSerieMap(data);
				}
				
			} else {
				console.log(data);
				throw 'invalid data';
			}
			
		},
		
		
		
		/*
		
		[{
			name: '',
			data: []
		}]
		
		*/
		fromSerieArray : function(data){
			// check the data points
			var seriesToRemove = [];
			data.forEach(function(serie, index){
				
				if(serie.data && serie.data.length>1){
					var point0 = serie.data[0], x0, y0, pointType, dataPoints = serie.data, ok = true, xLabel = null, yLabel = null;
					
					if(Array.isArray(point0)){
						pointType = 'array';
						xLabel = 0;
						yLabel = 1;
					} else {
						pointType = 'object';
						// detect the date & value fields
						if(point0.hasOwnProperty('y')) yLabel = 'y';
						Object.keys(point0).forEach(function(key){
							if(DataReader.dateFields.indexOf(key.toLowerCase()) !== -1){
								if(!xLabel) xLabel = key;
							} else if(!yLabel){
								yLabel = key;
							}
						});
					}
					
					if(xLabel===null || yLabel===null)
						console.log('serie '+serie.name+' : invalid data');
					
					x0 = point0[xLabel];
					y0 = point0[yLabel];
					
					var typeofY0 = typeof y0;
					y0 = Number(y0);
					if(isNaN(y0)){
						console.log('serie '+serie.name+' : y values are not numbers');
						seriesToRemove.push(index);
						ok = false;
					} else {
						
						// date field
						if(typeof x0 === 'number'){
							// must be timestamp
							// try to detect non milliseconds timestamps
							if(x0 < (Date.now() - 315576000000)){
								for(var i=0; i<dataPoints.length; i++)
									dataPoints[i][xLabel] *= 1000;
							}
						} else if(typeof x0 === 'string'){
							
							x0 = Date.parse(x0);
							if(isNaN(x0)){
								console.log('serie '+serie.name+' : x values are not dates');
								seriesToRemove.push(index);
								ok = false;
							} else {
								for(var i=0; i<dataPoints.length; i++)
									dataPoints[i][xLabel] = Date.parse(dataPoints[i][xLabel]);
							}
							
						} else {
							console.log('serie '+serie.name+' : invalid x values');
							seriesToRemove.push(index);
							ok = false;
						}
						
					}
					
					if(ok && typeofY0 != 'number'){
						// convert y values
						for(var i=0; i<dataPoints.length; i++)
							dataPoints[i][yLabel] = Number(dataPoints[i][yLabel]);
					}
					
					if(ok && pointType==='object' && xLabel!='x'){
						for(var i=0; i<dataPoints.length; i++){
							dataPoints[i].x = dataPoints[i][xLabel];
							delete dataPoints[i][xLabel];
						}
					}
					
					if(ok && pointType==='object' && yLabel!='y'){
						for(var i=0; i<dataPoints.length; i++){
							dataPoints[i].y = dataPoints[i][yLabel];
							delete dataPoints[i][yLabel];
						}
					}
					
				} else {
					// empty serie
					console.log('serie '+serie.name+' : no data');
					seriesToRemove.push(index);
				}
				
			});
			
			for(var i = seriesToRemove.length - 1; i>=0; i--){
				data.splice(seriesToRemove[i],1);
			}
			
			return data;
		},
		
		/*
		
		{
			'serie' : [data]
		}
		
		*/
		fromSerieMap : function(data){
			var o = [];
			for(serieName in data){
				o.push({
					name: serieName,
					data: data[serieName]
				});
			}
			return DataReader.fromSerieArray(o);
		},
		
		/*
		
		{
			name: '',
			data: []
		}
		
		*/
		fromSerieObj : function(data){
			return DataReader.fromSerieArray([data]);
		},
		
		/*
		
		[data]
		
		*/
		fromDataArray : function(data){
			return DataReader.fromSerieObj({
				name: 'serie1',
				data: data
			});
		},
		
		
		/*
		
		[{
			date: // x
			serie1: // data of serie1
			serie2: // data of serie2
			...
		}]
		
		*/
		dateFields: ['date', 'x', 'datetime', 'time'],
		fromDataArrayObj : function(data){
			var seriesData = {}, x, y, dateField = null;
			
			// detect the date field
			Object.keys(data[0]).forEach(function(key){
				if(DataReader.dateFields.indexOf(key.toLowerCase()) !== -1){
					dateField = key;
					return false;
				}
			});
			
			if(dateField===null){
				console.log(data);
				throw 'invalid data';
			}
			
			data.forEach(function(point){
				
				x = point[dateField];
				for(var field in point){
					if(field === dateField) continue;
					
					y = point[field];
					
					if(!seriesData.hasOwnProperty(field))
						seriesData[field] = [];
					
					seriesData[field].push([x,y]);
					
				}
				
			});
			
			return DataReader.fromSerieMap(seriesData);
		}
		
		
	};
	
	
	
	/* register as a plugin in jQuery */
	$.fn.plot = function(){
		var args = [].slice.call(arguments);
		
		if (this[0]) { // this[0] is the renderTo div
			
			var instance = $(this[0]).data('plot');
			
			if(instance){
				if(args.length){
					if(typeof args[0] == 'string'){
						// access the attribute or method
						var prop = instance[args.shift()];
						if(typeof prop == 'function'){
							var r = prop.apply(instance,args);
							return (r === instance) ? this : r; // make it chainable
						}
						else {
							if(args.length==0){
								// getter
								return prop;
							}
							else if(args.length==1){
								// setter
								prop = args[0];
								return this;
							}
						}
					}
				}
				else
					return instance;// When called without parameters return the instance
			}
			
			// if we are are, it means that there is no instance or that the user wants to create a new one !
			// /!\ NOTE : be sure to not emit any event in the constructor, or delay them using the setTimeout function !
			instance = new Plot(this[0],args[0],args[1],args[2],args[3],args[4],args[5],args[6]);
			$(this[0]).data('plot',instance);
			
			return this;
		}
	};
	
	return Plot;
	
	
}));