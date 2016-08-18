(function(){
	
	
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
			view: new $.Table.TableView({
				fields:{
					'__check':{
						hidden: true
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
						class: 'date'
					}
				},
				selectable:{
					check: true
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
			readonly: false
		},opt);
		
		this._table = options.table;
		
		if(this._table instanceof EThing.Table){
			delete options.table;
			if(!options.model)
				options.model = new TableModel(this._table);
		}
		
		
		$.Table.call(this,element,options);
		
		this.$element.find('table').addClass('table table-hover');
		
		// add specific actions :
		var actions = {
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
					
					var $html = $('<div><textarea class="form-control" placeholder="field == value"></textarea><div class="alert alert-danger" role="alert" style="display: none;"></div></div>'),
						currentFileter = self.model().filter();
					
					if(currentFileter)
						$html.find('textarea').val(currentFileter);
					
					$html.find('textarea').change(function(){
						$html.find('.alert').hide();
					});
					
					$html.modal({
						title: 'Filter data',
						buttons: {
							'+Filter': function(){
								var query = $html.find('textarea').val(), $this = $(this);
								self.model().filter(query);
								self.reload().done(function(){
									$this.modal('hide');
								}).fail(function(e){
									$html.find('.alert').html(e.message).show();
								});
								return false;
							},
							'Cancel': null
						}
					});
				},
				icon: 'filter',
				tooltip: 'apply a filter'
			} : null,
			'add':this._table && !this.options.readonly ? {
				fn: function(){
					
					var table = self._table,
						$html = $('<div class="container-fluid">');
					
					var addField = function(){
						
						var $row = $('<div class="row">'+
									  '<div class="col-sm-5">'+
										'<div class="input-group field">'+
										  '<input type="text" class="form-control" placeholder="field">'+
										  '<div class="input-group-btn">'+
											'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><span class="caret"></span></button>'+
											'<ul class="dropdown-menu dropdown-menu-right">'+
											'</ul>'+
										  '</div>'+
										'</div>'+
									  '</div>'+
									  '<div class="col-sm-6">'+
										'<div class="input-group value">'+
										  '<div class="input-group-btn">'+
											'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><span class="type">String</span> <span class="caret"></span></button>'+
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
									  '<div class="col-sm-1">'+
										'<button type="button" class="btn btn-default" data-role="remove"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span></button>'+
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
							$('<button type="button" class="btn btn-default"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> field</button>').click(addField)
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
			} : null
		},
		$actions = this.$element.find('div[name="actions"]');
		
		for(var i in actions){
			$('<button type="button" class="btn btn-default" data-name="'+i+'">')
				.append('<span class="glyphicon glyphicon-'+actions[i].icon+'" aria-hidden="true">')
				.click(actions[i].fn)
				.tooltip({
					container: this.$element,
					trigger:'hover',
					placement: 'bottom',
					title: actions[i].tooltip
				})
				.appendTo($actions);
		}
		
		$actions.find('[data-name="remove"]').hide();
		
		
	}
	inherits(TableViewer,$.Table);
	
	
	
	
	var TableModel = function(options){
		if(options instanceof EThing.Table)
			options = {
				table: options
			};
		
		this._options = $.extend(true,{
			table: null
		},options);
		
		$.Table.Model.call(this,this._options);
		
		this._table = this._options.table;
		this._sort = null;
		this._filter = null;
	}
	inherits(TableModel,$.Table.Model);
	
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
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery)
		window.jQuery.addPlugin('TableViewer',TableViewer);
	

})();
