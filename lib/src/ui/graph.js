(function(){


var dependency = $.Dependency({
	url: '//code.highcharts.com/stock/highstock.js',
	then: '//code.highcharts.com/stock/modules/exporting.js'
});


// the second arg must be a Table resource or an option object 
var Graph = function(element, options) {
	
	$.AbstractPlugin.call(this,element);
	
	
	this.$element.empty().addClass('Graph')
	
	var _defaultOpt = {
			/* internal */
			splitInPanes: false,
			highstock: true,
			
			/* highcharts */
			chart: {
				type: 'spline',
				zoomType: 'x'
			},
			rangeSelector : {
                buttons: [{
                    type: 'day',
                    count: 1,
                    text: 'Day'
                }, {
                    type: 'day',
                    count: 7,
                    text: 'Week'
                }, {
                    type: 'month',
                    count: 1,
                    text: 'Month'
                }, {
                    type: 'all',
                    text: 'All'
                }],
                buttonTheme: {
                    width: 60
                },
                selected: 0
            },
			title: {
				text: null
			},
			navigator : {
				enabled : true
			},
			xAxis: {
				type: 'datetime',
				title: {
					text: 'time'
				},
				ordinal: false
			},
			plotOptions: {
				spline: {
					marker: {
						enabled: true
					}
				}
			},
			series: [],
			yAxis: [],
			credits: {
				enabled: false
			},
			exporting:{
				buttons:{
					contextButton:{
						menuItems: null
					}
				}
			},	
			navigation: {
				menuItemStyle: {
					fontWeight: 'normal',
					background: 'none'
				},
				menuItemHoverStyle: {
					fontWeight: 'bold',
					background: 'none',
					color: 'black'
				}
			}
		},
		_defaultyAxis = {
			alternateGridColor: '#FDFFD5'
		},
		_defaultSerie = {
		
		}
		_opt = null,
		_self = this;





	var loader = function() {
		return $('<div style="text-align: center;margin: 40px;">loading ...</div>');
	}

	var printError = function(message){
		this.$element.empty().append('<div style="margin:10px;">'+message+'</div>');
		throw message;
	}


	this.open = function(options) {
		
		var self = this;
		
		if(options instanceof EThing.Table)
			options = Graph.defaultOptionsFromTable(options);
		
		_opt = $.extend(true,{}, _defaultOpt, options);
		
		if (!_opt.series || _opt.series.length == 0) {
			printError('no series to plot.');
			return;
		}
		
		var navigatorSeries = [], hasNavigator = _opt.navigator.enabled;
		
		var $loader = loader().appendTo(this.$element.empty());
		
		// extend default
		for(var i=0; i<_opt.series.length; i++)
			_opt.series[i] = $.extend(true,{},_defaultSerie,_opt.series[i]);
		for(var i=0; i<_opt.yAxis.length; i++)
			_opt.yAxis[i] = $.extend(true,{},_defaultyAxis,_opt.yAxis[i]);
		
		
		
		// download the necessary data
		var dataLoader = new DataLoader();
		for(var i=0; i<_opt.series.length; i++){
			if($.isPlainObject(_opt.series[i].data) && _opt.series[i].data.hasOwnProperty('tableId') && _opt.series[i].data.hasOwnProperty('field')){
				var table = _opt.series[i].data.tableId,
					field = _opt.series[i].data.field,
					length = _opt.series[i].data.length;
				
				dataLoader.add(table,field,length);
			}
		}
		
		
		var instanciate = function(){
			$loader.remove();
			
			Highcharts.setOptions({
				global: {
					useUTC: false
				}
			});
			
			
			/*
			Update the menu
			*/
			
			var popupOptions = function () {
				
				$('<div>')
					.graphWizard(options)
					.modal({
						title: "Graph ...",
						buttons: {
							'+graph': function(){
								var $this = $(this);
								$this.graphWizard().validate(function(options){
									$this.modal('hide',function(){
										new Graph(element, options);
									});
								});
								return false;
							},
							'Cancel': null
						}
					});
			};
			
			_opt.exporting.buttons.contextButton.menuItems = [].concat({
				text: 'Options',
				onclick: popupOptions
			}, _opt.exporting.buttons.contextButton.menuItems || Highcharts.getOptions().exporting.buttons.contextButton.menuItems);
			
			
			try {
				
				if(hasNavigator)
					$.extend(true,_opt,{
						navigator:{
							series: {
								data: navigatorSeries[0],
								type: 'spline'
							}
						}
					});
				
				var $g = $('<div class="chart"></div>')
					.appendTo(self.$element)
					.highcharts( _opt.highstock ? 'StockChart' : 'Chart',_opt,function(chart){
						
						if(hasNavigator)
							for(var i=1; i<navigatorSeries.length; i++)
								chart.addSeries({
									enableMouseTracking: false,
									data: navigatorSeries[i],
									xAxis:'navigator-x-axis',
									yAxis: 'navigator-y-axis',
									name: null,
									isInternal: true,
									showInLegend: false,
									color: chart.series[i].color,
									type: 'spline',
									fillOpacity: 0.05,
									dataGrouping: {
										smoothed: true
									},
									lineWidth: 1,
									marker: {
										enabled: false
									}
								});
						
					});
			}
			catch(e){
				console.log(e);
				self.$element.html(e);
			}
			
		};
		
		
		dataLoader.submit(function(){
			
			// all the data are loaded
			
			// replace the table/field object by its data
			for(var i=0; i<_opt.series.length; i++){
				if($.isPlainObject(_opt.series[i].data)){
					var table = _opt.series[i].data.tableId,
						field = _opt.series[i].data.field,
						data = dataLoader.getData(table,field);
					
					
					// if empty data, remove this serie
					if(!data || !data.length){
						var removedSerie = _opt.series.splice(i, 1)[0];
						i--;
						
						// remove this yAxis if not shared with another serie
						var sharedyaxis = false;
						for(var j=0; j<_opt.series.length; j++)
							if(_opt.series[j].yAxis === removedSerie.yAxis){
								sharedyaxis = true;
								break;
							}
						if(!sharedyaxis){
							for(var j=0; j<_opt.yAxis.length; j++)
								if(_opt.yAxis[j].id === removedSerie.yAxis){
									_opt.yAxis.splice(j, 1);
									break;
								}
						}
						
						continue;
					}
					
					_opt.series[i].data = data;
					
					// create navigators series
					if(hasNavigator){
						// normalize
						var max = null, min = null, navdata = [], sampling = data.length > 100 ? Math.round(data.length / 100) : 1;
						for(var j=0; j<data.length; j++){
							if(j%sampling != 0)
								continue;
							if(max===null || data[j][1] > max)
								max = data[j][1];
							if(min===null || data[j][1] < min)
								min = data[j][1];
						}
						if(min === max){
							min -= 1;
							max += 1;
						}
						for(var j=0; j<data.length; j++){
							if(j%sampling != 0)
								continue;
							navdata.push([
								data[j][0],
								(data[j][1] - min) / (max - min)
							]);
						}
						navigatorSeries.push(navdata);
					}
					
				}
			}
			
			// split in panes
			if(_opt.splitInPanes){
				var marge = 5, // vertical space between 2 panes (in %)
					N = _opt.yAxis.length;// number of panes
				
				var panesHeight = (100-(N-1)*marge)/N;
				_opt.yAxis.forEach(function(yAxe, index){
					yAxe.height = panesHeight+'%';
					yAxe.top = (index*(panesHeight+marge))+'%';
					yAxe.offset = 0;
				});
				
			}
			
			// load the highcharts library
			dependency.require(instanciate);
			
		});

	};

	this.options = function(){
		return _opt;
	};
	
	this.chart = function(){
		return self.$element.children('.chart').highcharts();
	};

	this.open(options);

};

Graph.defaultOptionsFromTable = function(table, keysToPlot, length){
	
	if(arguments.length == 2 && typeof keysToPlot == 'number'){
		length = keysToPlot;
		keysToPlot = null;
	}
	
	var opt = {
		splitInPanes: true,
		title: {
			text: table.name()
		},
		series:[],
		yAxis:[]
	};
	
	var keys;
	if(Array.isArray(keysToPlot) && keysToPlot.length)
		keys = keysToPlot;
	else if (typeof keysToPlot == 'string')
		keys = [keysToPlot];
	else
		keys = table.keys();
	
	
	
	for(var i=0; i<keys.length; i++){
		
		var key = keys[i],
			axisId = 'axis'+i;
		
		opt.series.push({
			data: {
				tableId: table.id(),
				field: key,
				length: length
			},
			yAxis: axisId,
			name: key
		});
		
		opt.yAxis.push({
			id: axisId,
			title: {
				text: key
			}
		});
		
	}
	
	
	return opt;
}

/*
preset = {
	
	yAxis: [
		{
			id: "axis0",
			title: "field1"
		},
		...
	],
	series: [
		{
			data: {
				tableId: "tableId",
				field: "fieldName"
			},
			yAxis: "axis0"
		},
		...
	]
	
}
*/
var GraphWizard = function(element, preset) {
	
	$.AbstractPlugin.call(this,element);
	
	
	if(preset instanceof EThing.Table)
		preset = Graph.defaultOptionsFromTable(preset);
	
	preset = $.extend({
		series:[{}],
		yAxis:[{}]
	},preset);
		
	
	var MAX_SERIES = 5;
	var MAX_YAXIS = 5;
	
	this.$element.html(
	  '<ul class="nav nav-tabs" role="tablist">'+
		'<li role="presentation" class="active"><a href="#series" aria-controls="series" role="tab" data-toggle="tab">Series</a></li>'+
		'<li role="presentation"><a href="#yaxis" aria-controls="yaxis" role="tab" data-toggle="tab">y-Axis</a></li>'+
		'<li role="presentation"><a href="#appearance" aria-controls="appearance" role="tab" data-toggle="tab">Appearance</a></li>'+
	  '</ul>'+
	  '<div class="tab-content">'+
		'<div role="tabpanel" class="tab-pane active" id="series"><div id="series-list" style="margin:20px 0;"></div></div>'+
		'<div role="tabpanel" class="tab-pane" id="yaxis"><div id="yaxis-list" style="margin:20px 0;"></div></div>'+
		'<div role="tabpanel" class="tab-pane" id="appearance" style="margin:20px 0;"></div>'+
	  '</div>'
	);
	
	var yaxisIndex = 0,
		seriesIndex = 0,
		$series = function(){
			return $('div.serie',$('#series-list',self.$element));
		},
		$yaxis = function(){
			return $('div.yAxis',$('#yaxis-list',self.$element));
		},
		self = this;
	
	this.addSerie = function(value){
		
		var $form = $('<div>').form({
			'name':{
				input: 'text',
				validator: $.Form.validator.NotEmpty
			},
			'data': new $.Form.TableFieldSelect({
				onChange: function(table,field){
					var item = this.form().findItem('name');
					if(item)
						item.setValue(field);
				}
			}),
			'yAxis':{
				input: '<select>',
				attr: {
					name: "yaxis"
				},
				get: function($e){
					var v = $e.val();
					if(v===null || v=="_")
						throw "no y-Axis selected";
					
					return String(v);
				}
			},
			'type':{
				input: ['line','spline','area','areaspline','column','scatter']
			}
			
		});
		
		var form = $form.form();
		
		var $serieHtml = $('<div class="panel panel-default serie">').append(
			$('<div class="panel-heading"></div>').append(
				'Serie #'+(++seriesIndex),
				$('<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>').css({
					float: 'right',
					cursor: 'pointer'
				}).click(function(){
					// self destruction !
					$serieHtml.remove();
					update();
				})
			),
			$('<div class="panel-body">').append($form)
		).appendTo($('#series-list',this.$element)).data('form',form).data('id',seriesIndex).attr('name',seriesIndex);
		
		update();
		
		if(value)
			form.setValue(value);
		
		return form;
	};
	
	this.addyAxis = function(value){
		
		var $form = $('<div>').form(new $.Form.FormLayout([{
			name: 'title',
			item: {
				input: function(){
					return $('<input type="text">').change(update);
				},
				get: function($e){
					var v = $e.val().trim();
					if(!v)
						throw "the name must not be empty";
					return {text:v};
				},
				set:function($e,v){
					if(typeof v == 'string')
						$e.val(v);
					else if($.isPlainObject(v) && v.hasOwnProperty('text')){
						$e.val(v.text);
					}
				},
				value: "a.u."
			}
		},{
			name: 'id',
			item: {
				input: 'text',
				value: "axis"+yaxisIndex
			},
			hidden: true
		}]));
		
		var form = $form.form();
		
		if(value)
			form.setValue(value);
		
		var $yAxisHtml = $('<div class="panel panel-default yAxis">').append(
			$('<div class="panel-heading"></div>').append(
				'Y-Axis #'+(yaxisIndex+1),
				$('<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>').css({
					float: 'right',
					cursor: 'pointer'
				}).click(function(){
					// self destruction !
					$yAxisHtml.remove();
					update();
				})
			),
			$('<div class="panel-body">').append($form)
		).appendTo($('#yaxis-list',this.$element)).data('form',form).data('id',yaxisIndex).attr('name',yaxisIndex);
		
		yaxisIndex++;
		
		update();
		
		return form;
	};
	
	var update = function(){
		
		// 1 - list the available y-Axis
		var $options = ['<option selected disabled value="_">select ...</option>'];
		$yaxis().each(function(){
			
			var id = $(this).data('id'),
				form = $(this).data('form'),
				titleItem = form.findItem('title'),
				name = titleItem.getValue().text;
			
			$options.push('<option value="axis'+id+'">#'+(id+1)+(name.length ? ' ['+name+']' : '')+'</option>');
		});
		
		
		// update the yaxis select element
		$series().each(function(){
			var form = $(this).data('form'),
				$input = form.findItem('yAxis').input(),
				save = $input.val();
			$input.empty().append($options).val(save);
		});
		
		
		// update other things
		if($series().length>MAX_SERIES)
			$('#series-add',self.$element).hide();
		else
			$('#series-add',self.$element).show();
		
		
		if($yaxis().length>MAX_YAXIS)
			$('#yaxis-add',self.$element).hide();
		else
			$('#yaxis-add',self.$element).show();
		
	}
	
	
	$('#series',this.$element).append($('<div id="series-add" style="cursor: pointer;color: #5CAEF2;">+ Add a serie</div>').click(function(){self.addSerie();}));
	$('#yaxis',this.$element).append($('<div id="yaxis-add" style="cursor: pointer;color: #5CAEF2;">+ Add an Y-Axis</div>').click(function(){self.addyAxis();}));
	
	
	
	
	
	// appearance
	
	var $formAppearance = $('#appearance',this.$element).form(new $.Form.FormLayout([{
		name: 'title',
		item: {
			input: 'text',
			validator: $.Form.validator.NotEmpty,
			set:function($e,v){
				if(typeof v == 'string')
					$e.val(v);
				else if($.isPlainObject(v) && v.hasOwnProperty('text')){
					$e.val(v.text);
				}
			}
		},
		checkable:true,
		checked:false
	},{
		name: 'subtitle',
		item:{
			input: 'text',
			validator: $.Form.validator.NotEmpty,
			set:function($e,v){
				if(typeof v == 'string')
					$e.val(v);
				else if($.isPlainObject(v) && v.hasOwnProperty('text')){
					$e.val(v.text);
				}
			}
		},
		checkable:true,
		checked:false
	}]));
	
	var formAppearance = $formAppearance.form();
	
	
	
	this.validate = function(callback){
		
		var data = {
			splitInPanes: true,
			series:[],
			yAxis:[]
		},
		self=this,
		yAxisAvailableList = [],
		promises = [];
		
		// validate the yaxis
		$yaxis().each(function(){
			promises.push(
				$(this).data('form').validate().done(function(d){
					yAxisAvailableList.push(d);
				})
			);
		});
		
		// validate the series
		$series().each(function(){
			promises.push(
				$(this).data('form').validate().done(function(d){
					// is the yAxis used already in the list ?
					var inList = false;
					for(var i=0; i<data.yAxis.length; i++)
						if(data.yAxis[i].id === d.yAxis){
							inList = true;
							break;
						}
					if(!inList){
						// add the yaxis
						for(var i=0; i<yAxisAvailableList.length; i++)
							if(yAxisAvailableList[i].id === d.yAxis){
								data.yAxis.push(yAxisAvailableList[i]);
								break;
							}
					}
					data.series.push(d);
				})
			);
		});
		
		
		promises.push(
			formAppearance.validate().done(function(d){
				$.extend(data,d);
			})
		);
		
		$.when.apply($, promises).done(function() {
			if(typeof callback == 'function'){
				callback.call(self,data);
			}
		})
	};
	
	
	
	
	if(preset){
		
		if($.isArray(preset.yAxis))
			for(var i=0; i<preset.yAxis.length; i++)
				this.addyAxis(preset.yAxis[i]);
		
		if($.isArray(preset.series))
			for(var i=0; i<preset.series.length; i++)
				this.addSerie(preset.series[i]);
		
		// other
		formAppearance.setValue(preset);
	}
	
};


var GraphSimpleWizard = function(element, table) {
	
	$.AbstractPlugin.call(this,element);
	
	this.$element.addClass('SimpleGraphBuilder');
	
	var keys = table.keys();
	
	var $fields = $('<div>').appendTo(this.$element);
	for(var i=0; i<keys.length; i++){
		var $row = $('<div>').append('<label><input type="checkbox" data-value="'+encodeURIComponent(keys[i])+'"> '+keys[i]+'</label>').appendTo($fields);
	}
	
	this.$message = $('<div class="alert alert-danger" role="alert">').hide().appendTo(this.$element);
	
	this.validate = function(callback){
		this.$message.hide();
		
		// get the selected fields
		var selectedFields = [];
		this.$element.find('input[type="checkbox"]:checked').each(function(){
			selectedFields.push( decodeURIComponent($(this).attr('data-value')) );
		});
		
		
		if( selectedFields.length == 0 ){
			this.$message.html('Please, select at least one field').show();
			return;
		}
		
		var opt = Graph.defaultOptionsFromTable(table, selectedFields);
		
		if(typeof callback == 'function'){
			callback.call(this,opt);
		}
		
		return opt;
	};
	
	
}



DataLoader = function(){
	this._list = {};
};
DataLoader.prototype.add = function(table,field,length){
	
	if(table instanceof EThing.Table)
		table = table.id();
	
	if(!this._list[table])
		this._list[table] = {
			fields:[],
			length: 0, // 0 means all the available, n > 0 means n last data
			data:null,
			status: "wait"
		};
	
	if((typeof length == 'number') && length > this._list[table].length)
		this._list[table].length = length;
	
	if($.inArray(field, this._list[table].fields)==-1)
		this._list[table].fields.push(field);
	
}
DataLoader.prototype.getData = function(table,field){
	
	var data = null;
	
	if(table instanceof EThing.Table)
		table = table.id();
	
	if(this._list[table] && $.inArray(field, this._list[table].fields)>=0 && this._list[table].status == "done"){
		
		data = [],
		d = this._list[table].data;
		
		for(var i=0; i<d.length; i++){
			var point = d[i],
				val = parseFloat(point[field]);
			if(!isNaN(val))
				data.push([Date.parse(point['date']), val]);
		}
		
	}
	
	return data;
}
DataLoader.prototype.submit = function(callback){
	var deferreds = [],
		self = this;
	
	for(var tableId in this._list){
		deferreds.push(EThing.Table.select(tableId, this._list[tableId].length ? {
			start: -this._list[tableId].length
		} : null));
	}
	
	return $.when.apply($, deferreds).always(function(a,b,c) {
		
		var d = [];
		
		if(deferreds.length == 1)
			d.push(arguments[0]);
		else if(deferreds.length>1)
			for(var i=0; i<arguments.length; i++)
				d.push(arguments[i][0]);
		
		var i=0;
		for(var tableId in self._list){
			
			if(d[i]!==null){
				self._list[tableId].data = d[i];
				self._list[tableId].status = "done";
			}
			else
				self._list[tableId].status = "error";
			i++;
		}
		
		if($.isFunction(callback))
			callback.call(this);
	});
	
	
}


/* register as a plugin in jQuery */
if (window.jQuery) {
	window.jQuery.addPlugin('Graph',Graph);
	window.jQuery.addPlugin('GraphSimpleWizard',GraphSimpleWizard);
	window.jQuery.addPlugin('GraphWizard',GraphWizard);
}



})();
