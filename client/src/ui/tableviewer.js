(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'table', 'ething', './core', './modal', 'css!bootstrap-toggle-flat', 'css!./tableviewer'], factory);
    } else {
        // Browser globals
        root.TableViewer = factory(root.jQuery, root.Table, root.EThing);
    }
}(this, function ($, Table, EThing, UI) {
	
	var isTouchDevice = navigator ? (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase())) : false;
	
	function inherits(extended, parent){
		extended.prototype = Object.create(parent.prototype);
	};
	
	
	function TableViewer(element,opt){
		
		var self = this;
		
		if(opt instanceof EThing.Table)
			opt = {
				table: opt
			};
		
		var options = $.extend(true,{
			table: null,
			view: new EditableTableView({
				fields:{
					'__check':{
						hidden: true,
						editable: false
					},
					'date':{
						formatter: function(d){
							function pad(n, width, z) {
								z = z || '0';
								n = n + '';
								return n.length >= width ? n : new Array(width - n.length + 1)
									.join(z) + n;
							}
							return pad(d.getFullYear(), 4) + '/' + pad(d.getMonth() + 1, 2) + '/' + pad(d.getDate(), 2) + ' ' + pad(d.getHours(), 2) + ':' + pad(d.getMinutes(), 2) + ':' + pad(d.getSeconds(), 2);
						},
						class: 'date',
						editable: false
					}
				},
				selectable:{
					check: true,
					cumul: true,
					trigger: false
				}
			}),
			selectable:{
				enable: true,
				limit: null,
				trigger: null
			},
			pagination:{
				itemsPerPage: [20,50,100,'all'], // may be an array of available values [20,50,100,'all']
				enable: true // enable the pagination
			},
			sortBy: '-date',
			class: 'tableviewer',
			readonly: false,
			actions: null // see below
		},opt);
		
		this._table = options.table;
		
		if(this._table instanceof EThing.Table){
			delete options.table;
			if(!options.model)
				options.model = new TableModel(this._table);
		}
		
		
		Table.call(this,element,options);
		
		this.$element.find('table').addClass('table table-hover');
		
		// add specific actions :
		var actions = $.extend(true,{
			'col-select':{
				html: function(){
					
					var self = this;
					var columnNames = this.model().keys();
					
					var $html = $(
						'<div class="btn-group btn-group-sm">'+
						  '<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'+
							'<span class="glyphicon glyphicon-resize-horizontal" aria-hidden="true"></span>'+
						  '</button>'+
						  '<ul class="dropdown-menu"></ul>'+
						'</div>'
					);
					
					// do not close the menu on click
					$html.find('.dropdown-menu').on('click', 'li', function (e) {
					  e.stopPropagation();
					});
					
					$html.find('.dropdown-menu').on('mouseenter mouseleave ', function (e) {
					  e.stopPropagation(); // avoid tooltip on the dropdown menu
					});
					
					columnNames.forEach(function(columnName){
						var $li = $('<li><div class="checkbox checkbox-slider--c checkbox-slider-sm"><label><input type="checkbox" checked><span>'+columnName+'</span></label></div></li>');
						$li.find('input').change(function(){
							var checked = $(this).prop('checked');
							
							self.view().setVisible(columnName, checked);
							
						});
						$html.find('ul').append($li);
					}, this);
					
					return $html;
				},
				tooltip: 'show/hide columns'
			},
			'update':{
				fn: function(){
					self.reload();
				},
				icon: 'repeat',
				tooltip: 'reload the data'
			},
			'edit':this._table && !this.options.readonly ? {
				fn: function(){
					self.view().setVisible('__check',!self.view().isVisible('__check'));
					$actions.find('[data-name="remove"]').toggle();
				},
				icon: 'check',
				tooltip: 'edit the table'
			} : null,
			'remove':this._table && !this.options.readonly ? {
				fn: function(){
					var selection = self.selection();
					if(selection.length){
						if(confirm('Remove the '+selection.length+' selected row(s) ?')){
							var ids = selection.map(function(el){
								return el.id;
							});
							self._table.removeRow(ids,function(){
								// reload the table
								self.reload();
							});
						}
					}
					else
						alert('No rows selected.');
				},
				icon: 'trash',
				tooltip: 'remove the selected rows'
			} : null,
			'filter':this._table ? {
				fn: function(){
					
					var $html = $('<div>'+
						"<p>You can filter table's rows using a search query combining one or more search clauses. <a data-role=\"filter-show-details\" href=\"#\">more...</a></p>"+
						'<div data-role="filter-details" style="display: none;">'+
							"<p>Each search clause is made up of three parts :</p>"+
							'<ul>'+
								"<li>Field : it corresponds to the column's name.</li>"+
								'<li>Operator : test that is performed on the data to provide a match.</li>'+
								'<li>Value : The content of the field that is tested.</li>'+
							'</ul>'+
							'<p>Combine clauses with the conjunctions "and" or "or".</p>'+
							
							"<p>The available operators :</p>"+
							"<ul>"+
								"<li>'==' : equal to ... This operator is compatible with any types of value.</li>"+
								"<li>'!=' : not equal to ... This operator is compatible with any types of value.</li>"+
								"<li>'is' : is of type ... This operator is compatible with any types of value.</li>"+
								"<li>'&gt;' : greater than ... This operator is only compatible with numbers or dates.</li>"+
								"<li>'&lt;' : less than ... This operator is only compatible with numbers or dates.</li>"+
								"<li>'&gt;=' : greater than or equal to ... This operator is only compatible with numbers.</li>"+
								"<li>'&lt;=' : less than or equal to ... This operator is only compatible with numbers.</li>"+
								"<li>'^=' : start with ... This operator is only compatible with strings.</li>"+
								"<li>'$=' : end with ... This operator is only compatible with strings.</li>"+
								"<li>'*=' : contain ... This operator is only compatible with strings.</li>"+
								"<li>'~=' : contain the word ... This operator is only compatible with strings.</li>"+
							"</ul>"+
						'</div>'+
						
						"<p>"+
							"example:"+
						"</p>"+
						"<p>"+
							"<code>date &gt; '2016-03-04T00:00:00+01:00' AND temperature &lt; 20.5</code>"+
						"</p>"+
						
						'<p><textarea class="form-control" placeholder="field == value"></textarea></p><div class="alert alert-danger" role="alert" style="display: none;"></div></div>'),
						currentFilter = self.model().filter();
					
					if(currentFilter)
						$html.find('textarea').val(currentFilter);
					
					$html.find('textarea').change(function(){
						$html.find('.alert').hide();
					});
					
					$html.find('a[data-role="filter-show-details"]').click(function(e){
						e.preventDefault();
						var $target = $('div[data-role="filter-details"]',$html);
						$target.slideToggle().data('state',!$target.data('state'));
						$(this).html( $target.data('state') ? 'hide' : 'more...' );
					})
					
					function updateFilterButtonState(){
						var filtered = (self.model().filter()||'').trim() != '';
						self.$element.find('[name="actions"] button[data-name="filter"]').toggleClass('btn-default',!filtered).toggleClass('btn-primary',filtered);
					}
					
					$html.modal({
						title: 'Filter data',
						buttons: {
							'+Filter': function(){
								var query = $html.find('textarea').val(), $this = $(this);
								self.model().filter(query);
								self.reload().done(function(){
									updateFilterButtonState();
									$this.modal('hide');
								}).fail(function(e){
									$html.find('.alert').html(e.message).show();
								});
								return false;
							},
							'Cancel': updateFilterButtonState
						}
					});
				},
				icon: 'filter',
				tooltip: 'apply a filter'
			} : null,
			'add':this._table && !this.options.readonly ? {
				fn: function(){
					
					var table = self._table,
						$html = $('<div class="container-fluid tableviewer-add-data">');
					
					var addField = function(){
						
						var $row = $('<div class="row">'+
									  '<div class="col-sm-4">'+
										'<div class="input-group field">'+
										  '<input type="text" class="form-control" placeholder="field">'+
										  '<div class="input-group-btn">'+
											'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><span class="caret"></span></button>'+
											'<ul class="dropdown-menu dropdown-menu-right">'+
											'</ul>'+
										  '</div>'+
										'</div>'+
									  '</div>'+
									  '<div class="col-sm-6 col-md-7">'+
										'<div class="input-group value">'+
										  '<div class="input-group-btn">'+
											'<button type="button" data-role="type" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><span class="type">String</span> <span class="caret"></span></button>'+
											'<ul class="dropdown-menu">'+
											  '<li><a>String</a></li>'+
											  '<li><a>Number</a></li>'+
											  '<li><a>Boolean</a></li>'+
											  '<li><a>Text</a></li>'+
											'</ul>'+
										  '</div>'+
										  '<input type="text" class="form-control" placeholder="value">'+
										'</div>'+
									  '</div>'+
									  '<div class="col-sm-2 col-md-1">'+
										'<button type="button" class="btn btn-danger" data-role="remove"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span></button>'+
									  '</div>'+
									'</div>');
						
						
						var li = [], keys = table.keys();
						for(var i=0; i<keys.length; i++)
							li.push('<li><a>'+keys[i]+'</a></li>');
						$row.find('.field ul').append(li);
						
						$row.find('.value ul a').click(function(){

						  var type = $(this).text(),
							  $input = $(this).closest('.value').find('input,select,textarea'),
							  replace;
						  
						  $(this).closest('.value').find('span.type').text(type);
						  
						  switch(type.toLowerCase()){
							case 'string':
							  if(!$input.is('input[type="text"]'))
								replace = '<input type="text">';
							  break;
							case 'number':
							  if(!$input.is('input[type="number"]'))
								replace = '<input type="number" value="0">';
							  break;
							case 'boolean':
							  if(!$input.is('select'))
								replace = '<select><option>true</option><option>false</option></select>';
							  break;
							case 'text':
							  if(!$input.is('textarea'))
								replace = '<textarea>';
							  break;
						  }
						  
						  if(replace)
							$input.replaceWith($(replace).addClass('form-control'));
						  
						})

						$row.find('.field ul a').click(function(){
						  var fieldname = $(this).text();
						  $(this).closest('.field').find('input').val(fieldname);
						})
						
						$row.find('[data-role="remove"]').click(function(){
							$row.remove();
						});
						
						$row.insertBefore($html.children('.row').last());
						
					}
					
					var getValue = function(){
						var out = {}, err = false;
						
						$html.children('.row').each(function(){
							
							var $this = $(this),
								fieldname = $this.find('.field').find('input').val(),
								$input = $this.find('.value').find('input,select,textarea'),
								value;
							
							if(typeof fieldname == 'undefined')
								return;
							
							if(fieldname.length == 0){ // empty field name
								err = true;
								return;
							}
							
							if($input.is('input[type="number"]')){
								value = parseFloat($input.val()); // number
							}
							else if($input.is('select')){
								value = /true/i.test($input.val()); // boolean
							}
							else {
								value = $input.val(); // string
							}
							
							out[fieldname] = value;
							
						});
						
						if(Object.keys(out).length === 0)
							err = true;
						
						return err ? null : out;
					}
					
					$html.append( $('<div class="row row-top-space">').append(
						$('<div class="col-sm-1">').append(
							$('<button type="button" class="btn btn-success"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> field</button>').click(addField)
						)
					));
					
					// at 1 field by default
					addField();
					
					$html.modal({
						title: 'Add data',
						buttons: {
							'+Add': function(){
								var modal = this, data = getValue();
								if(data)
									table.insert(data).done(function(){
										$html.modal('hide');
										self.reload();
									});
								return false;
							},
							'Cancel': null
						},
						size: 'lg'
					});
					
					
				},
				icon: 'plus',
				tooltip: 'add data'
			} : null,
			'statistics': this._table && this._table.keys().length ? {
				fn: function(){
					var table = self._table,
						currentFilter = self.model().filter(),
						_this = this;
					
					if(!this.$html) this.$html = $(
							'<div class="container-fluid tableviewer-show-satistics">'+
								/*'<button class="btn btn-link" type="submit"><span class="glyphicon glyphicon-refresh" aria-hidden="true"></span> update</button>'+*/
								'<div class="input-group">'+
									'<input class="form-control" type="text" placeholder="Filter eg. date > \'12 hours ago\'">'+
									'<span class="input-group-btn">'+
										'<button class="btn btn-default" type="button">Update</button>'+
									'</span>'+
								'</div>'+
								'<div class="content"></div>'+
							'</div>'
						);
					
					
					function draw(){
						
						var $content = _this.$html.children('.content');
						
						$content.html('loading...');
						
						$.when.apply($, _this.statisticsDfrs).done(function(){
							
							$content.empty();
							
							for(var key in _this.statisticsObj){
								var $dl;
								
								if(_this.statisticsObj[key]){
									$dl = $('<dl class="dl-horizontal">');
									for(var n in _this.statisticsObj[key]){
										$dl.append('<dt>'+n+'</dt>', '<dd>'+_this.statisticsObj[key][n]+'</dd>');
									}
								} else {
									$dl = '<div class="alert alert-warning" role="alert">invalid, not numbers ?</div>';
								}
								
								$content.append('<h4>'+key+'</h4>', $dl);
							}
							
						}).fail(function(err){
							$content.html('error: '+err.message);
						});
					}
					
					function update(){
						_this.statisticsObj = {};
						var query = _this.$html.find('input').val() || '';
						_this.statisticsDfrs = table.keys().map(function(key){
							return table.computeStatistics(key, query).done(function(stats){
								_this.statisticsObj[key] = stats;
							});
						});
						
						draw();
					}
					
					this.$html.find('button').click(update);
					
					this.$html.find('input').keyup(function(e){
						if(e.keyCode == 13) update();
					}).val(currentFilter || '');
					
					this.statisticsDfrs ? draw() : update();
					
					this.$html.modal({
						title: 'Statistics',
						removeOnClose: 'detach',
						buttons: {
							'Close': null
						}
					});
					
				},
				icon: 'info-sign',
				tooltip: 'show statistics'
				
			} : null,
			'plot':{
				html: function(){
					
					var self = this;
					var columnNames = this.model().keys().filter(function(col){
						return col!=='date';
					});
					
					if(columnNames.length==0) return false;
					else if(columnNames.length==1){
						return $('<button type="button" class="btn btn-default">')
							.append('<span class="glyphicon glyphicon-stats" aria-hidden="true"></span>')
							.click(function(){
								UI.go('plot',{
									rid: self.model().getTableResource().id()
								});
							});
					} else {
						
						var $html = $(
							'<div class="btn-group btn-group-sm">'+
							  '<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'+
								'<span class="glyphicon glyphicon-stats" aria-hidden="true"></span>'+
							  '</button>'+
							  '<ul class="dropdown-menu"></ul>'+
							'</div>'
						);
						
						// do not close the menu on click
						$html.find('.dropdown-menu').on('click', 'li', function (e) {
						  e.stopPropagation();
						});
						
						$html.find('.dropdown-menu').on('mouseenter mouseleave ', function (e) {
						  e.stopPropagation(); // avoid tooltip on the dropdown menu
						});
						
						function updatePlotBtn(){
							$html.find('input[type="checkbox"]').filter(function(){
								return $(this).prop('checked');
							}).length > 0 ? $html.find('button').removeAttr('disabled') : $html.find('button').attr('disabled',"disabled");
						}
						
						columnNames.forEach(function(columnName){
							var $li = $('<li><div class="checkbox checkbox-slider--b-flat"><label><input type="checkbox" checked><span>'+columnName+'</span></label></div></li>');
							$li.find('input').prop('name',columnName).click(updatePlotBtn);
							$html.find('ul').append($li);
						});
						
						// trace btn
						var $li = $('<li><button type="button" class="btn btn-success btn-block btn-sm">plot</button></li>');
						$li.find('button').click(function(){
							var colsToPlot = $html.find('input[type="checkbox"]').filter(function(){
								return $(this).prop('checked');
							}).map(function(){
								return $(this).prop('name');
							}).toArray();
							if(colsToPlot.length>0){
								UI.go('plot',{
									rid: self.model().getTableResource().id(),
									fields: colsToPlot.join(',')
								});
							}
						});
						$html.find('ul').append($li);
						
						updatePlotBtn();
						
						return $html;
					}
				},
				tooltip: 'plot'
			}
		}, options.actions || null);
		
		var $actions = this.$element.find('div[name="actions"]');
		
		var $actionsRight = $('<div class="btn-group btn-group-sm pull-right" role="group">').appendTo($actions.parent());
		
		if(this._table instanceof EThing.Table){
			$('<div name="tablename" class="hidden-xs">').text(this._table.name()).insertAfter($actions);
		}
		
		Object.keys(actions).forEach(function(name){
			
			var action = actions[name];
			
			if(!action) return;
			
			var $button;
			
			if(typeof action.html == 'function'){
				$button = action.html.call(self, action);
			} else {
				var $icon = typeof action.icon === 'string' && !/</.test(action.icon) ? $('<span class="glyphicon glyphicon-'+action.icon+'" aria-hidden="true">') : $(action.icon);
				
				$button = $('<button type="button" class="btn btn-'+(action.buttonClass || 'default')+'">')
					.append($icon)
					.click(function(){
						action.fn.call(self, action);
					});
			}
			
			if(!$button) return;
			
			$button.attr('data-name',name);
			
			if(typeof action.tooltip == 'string' && !isTouchDevice)
				$button.tooltip({
					container: this.$element,
					trigger:'hover',
					placement: 'bottom',
					title: action.tooltip
				});
			
			$button.appendTo(action.right===true ? $actionsRight : $actions);
		}, this);
		
		$actions.find('[data-name="remove"]').hide();
		
		
	}
	inherits(TableViewer,Table);
	
	TableViewer.prototype.getTableResource = function(){
		return this._table;
	}
	
	
	var TableModel = function(options){
		if(options instanceof EThing.Table)
			options = {
				table: options
			};
		
		this._options = $.extend(true,{
			table: null
		},options);
		
		Table.Model.call(this,this._options);
		
		this._table = this._options.table;
		this._sort = null;
		this._filter = null;
	}
	inherits(TableModel,Table.Model);
	
	// return the keys/columns
	TableModel.prototype.keys = function(){
		var ks = this._table.keys();
		ks.unshift('date');
		return ks;
	}
	// return the number of rows, null if not known
	TableModel.prototype.rows = function(){
		return this._table.length();
	}
	// return the items, may be a deferred object
	// offset and length are used for pagination
	TableModel.prototype.data = function(parent, offset, length){
		var deferred = $.Deferred(),
			self = this;
		EThing.Table.select(this._table,{
			start: offset || 0,
			length: length || this._table.length(),
			sort: this._sort || "-date",
			query: this._filter
		})
			.done(function(items){
				deferred.resolve(
					items.map(function(item){
						item.date = new Date(item.date);
						return item;
					})
				);
			})
			.fail(function(e){
				deferred.reject(e);
			});
		
		return deferred;
	}
	// check if an item has children or not (tree model may have)
	TableModel.prototype.hasChildren = function(item){
		return false;
	}
	// sort the data
	TableModel.prototype.sort = function(field, ascending){
		this._sort = (ascending ? '+' : '-') + field;
	}
	// return a unique index identifying an items according to the data given in argument
	TableModel.prototype.index = function(tableItem){
		return tableItem.id;
	}
	TableModel.prototype.filter = function(query){
		if(typeof query == 'undefined')
			return this._filter;
		this._filter = (typeof query == 'string') ? query : null;
	}
	TableModel.prototype.getTableResource = function(){
		return this._table;
	}
	
	
	
	var EditableTableView = function(options){
		Table.TableView.call(this,options);
	}
	inherits(EditableTableView,Table.TableView);
	
	EditableTableView.prototype.createItem = function(item,index){
		/*var $tr = Table.TableView.prototype.createItem.call(this,item,index);
		return $tr;*/
		
		var self = this;
		
		// construct the item dom element
		var $tr = $('<tr>');
		
		Object.keys(this._fields).forEach(function(field){
			var fieldOptions = this._fields[field];
			if(fieldOptions.enable){
				var value = $.isFunction(fieldOptions.get) ? fieldOptions.get.call(this,item,index,$tr) : (
						(typeof item[field] != 'undefined') ? 
						($.isFunction(item[field]) ? item[field]() : item[field])
						: (fieldOptions.default===null ? "" : fieldOptions.default)
					);
				
				var formattedValue = value;
				if($.isFunction(fieldOptions.formatter))
					formattedValue = fieldOptions.formatter.call(this,value);
				
				
				var $td = $('<td>');
				
				$td
					.html( typeof formattedValue == 'object' ? formattedValue : formattedValue.toString() )
					.addClass(fieldOptions.class);
				
				if(fieldOptions.hidden)
					$td[0].style.display = "none";
				
				if(typeof fieldOptions.events == 'object')
					for(var eventName in fieldOptions.events){
						$td.on(eventName,{
							item: item
						},fieldOptions.events[eventName]);
					}
				
				if(typeof fieldOptions.editable === "undefined" || fieldOptions.editable){
					var $edit = $('<span class="glyphicon glyphicon-edit editabletableview-editcell" aria-hidden="true"></span>').click(function(){
						
						var $html = $(
							'<div class="container-fluid tableviewer-edit-cell">'+
								'<div class="input-group value">'+
								  '<div class="input-group-btn">'+
									'<button type="button" data-role="type" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><span class="type">String</span> <span class="caret"></span></button>'+
									'<ul class="dropdown-menu">'+
									  '<li><a>String</a></li>'+
									  '<li><a>Number</a></li>'+
									  '<li><a>Boolean</a></li>'+
									  '<li><a>Text</a></li>'+
									'</ul>'+
								  '</div>'+
								  '<input type="text" class="form-control" placeholder="value">'+
								'</div>'+
							'</div>'
						);
						
						$html.find('.value ul a').click(function(){
						  var type = $(this).text();
						  setType(type, value);
						});
						
						
						function setType(type, value){
							type = type.toLowerCase();
							if(['string','number','boolean','text'].indexOf(type)===-1) type = 'string';
							
							var $input = $html.find('.value').find('input,select,textarea'),
							  $replace = null,
							  valueType = typeof value;

							$html.find('.value').find('span.type').text(type.charAt(0).toUpperCase() + type.slice(1));

							switch(type){
								case 'string':
								  if(!$input.is('input[type="text"]')){
									$replace = $('<input type="text">');
									if(['string','number','boolean'].indexOf(valueType)!==-1) $replace.val(value+'');
								  }
								  break;
								case 'number':
								  if(!$input.is('input[type="number"]')){
									$replace = $('<input type="number" value="0">');
									if(['string','number'].indexOf(valueType)!==-1){
										var v = Number(value);
										if(!isNaN(v)) $replace.val(v);
									}
								  }
								  break;
								case 'boolean':
								  if(!$input.is('select')){
									$replace = $('<select><option>true</option><option>false</option></select>');
									if(['string','number','boolean'].indexOf(valueType)!==-1) $replace.val(!!value?'true':'false');
								  }
								  break;
								case 'text':
								  if(!$input.is('textarea')){
									$replace = $('<textarea>');
									if(['string','number','boolean'].indexOf(valueType)!==-1) $replace.val(value+'');
								  }
								  break;
							}
							
							
							if($replace){
								$replace.addClass('form-control');
								$input.replaceWith($replace);
								$input = $replace;
							}
						  
							return $input;
						}
						
						function setValue(value){
							var type = typeof value;
							var $input = setType(type);
							if(type === 'boolean'){
								$input.val(value?'true':'false');
							} else {
								$input.val(value);
							}
						}
						
						function getValue(){
							
							var $input = $html.find('.value').find('input,select,textarea'),
								value;
							
							if($input.is('input[type="number"]')){
								value = parseFloat($input.val()); // number
							}
							else if($input.is('select')){
								value = /true/i.test($input.val()); // boolean
							}
							else {
								value = $input.val(); // string
							}
							
							return value;
						}
						
						$html.modal({
							title: 'Edit cell',
							buttons: {
								'+Apply': function(){
									item[field] = getValue();
									self.table().getTableResource().replaceRow(item).done(function(){
										$html.modal('hide');
										self.table().reload();
									});
									return false;
								},
								'Cancel': null
							},
							size: 'lg'
						});
						
						setValue(value);
						
					});
					
					$td.hover(function(){
						$td.append($edit);
					}, function(){
						$edit.detach();
					});
				}
			
				$tr.append($td);
			}
		}, this);
		
		this._$tbody.append($tr);
		
		return $tr;
	}
	
	
	/* register as a plugin in jQuery */
	
	$.TableViewer = TableViewer;
	
	$.fn.tableViewer = function(){
		var args = [].slice.call(arguments);
		
		if (this[0]) { // this[0] is the renderTo div
			
			var instance = $(this[0]).data('tableViewer');
			
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
			instance = new TableViewer(this[0],args[0],args[1],args[2],args[3],args[4],args[5],args[6]);
			$(this[0]).data('tableViewer',instance);
			
			return this;
		}
	};
	
	
	return TableViewer;
	

}));
