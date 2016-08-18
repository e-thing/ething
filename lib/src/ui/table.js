(function(){
	
	
	
	/*
	events :
		- "selection.change" // is fired each time the selection change, (note: the selection is cleared when the page change or the data is reloaded
	*/
	
	var Table = function(element,opt){
		
		$.AbstractPlugin.call(this,element,$.extend(true,{
			model: null, // Model instance or array (will be converted into an ArrayModel, can be an URL pointing to JSON data)
			view: null, // View instance or options for the TableView 
			selectable: {
				enable: false, // enable selecting
				limit: 1, // limit the selection to a specific number, if 0 or null -> unlimited (for activating shift & ctrl selection, limit must be 0 or null)
				filter: null, // function(item) -> return boolean , if it returns false, this item is not selectable
				trigger: 'click', // null or 'click' only available value
				cumul: true // if true the selection is cumulative, else the selection is reset at every new selection
			},
			openable:{
				enable: true, // if the item has has children, open that children
				trigger: 'dbclick' // click or dbclick or any jquery event that are available on <tr> item
			},
			row: {
				class: null, // className(s) to be added to the table's item DOM element, multiple classname must be separated by space
				events: {}
			},
			before: null, // function, fired before the view and the model
			loaded: null, // function, fired when the browser has finished to load primary data
			error: null, // function, fired when the data could not have been loaded
			class: null, // className(s) to be added to the table DOM element, multiple classname must be separated by space
			pagination:{
				itemsPerPage: 20, // may be an array of available values [20,50,100,'all']
				enable: false // enable the pagination
			},
			sortBy: null, // can either be a string (ie: "+field" or "-field" or "field") or an object { field: "field", ascending: true|false }
			message: {
				empty: '<span class="tbl-message-warning">empty</span>',
				modelLoadError: '<span class="tbl-message-warning">error</span>',
				loading: '<span class="tbl-message-warning">loading...</span>'
			}
		},opt));
		
		var self = this;
		
		// some internal array
		this._items = [];
		this._map = [];
		
		
		
		
		// get the model
		this._model = (this.options.model instanceof Model) ? 
						this.options.model : 
						new ArrayModel( 
							(typeof this.options.model == 'string') ? 
							$.getJSON(this.options.model) : // if a string is given, assume it is an URL 
							this.options.model
						); // else must be an array
		
		
		
		
		/*
		dom building
		*/
		
		this.$element.empty().addClass('tbl').addClass(this.options.class);
		
		
		// construct the toolbar toolbar and prepend it to _$
		var hasToolbar = this.options.pagination.enable;
		if(hasToolbar){
			var $toolbar = $('<div class="tbl-toolbar toolbar btn-toolbar" role="toolbar">');
				
			// page length
			var itemsPerPage = this.options.pagination.itemsPerPage;
			if(!$.isArray(itemsPerPage))
				itemsPerPage = [itemsPerPage];
			var pageLengthTpl = (this.options.pagination.enable && itemsPerPage.length>1) ?
				'<div class="btn-group btn-group-sm" role="group" name="page-length">'+
					'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'+
						'<span><span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span> <span class="value"></span></span>'+
						'<span class="caret"></span>'+
					  '</button>'+
					 '<ul class="dropdown-menu"></ul>'+
				'</div>' : null;
			
			// pagination + go to page N
			var pageSelectorTpl = this.options.pagination.enable ?
				'<div name="pagination-div" class="btn-group btn-group-sm" role="group">'+
					  '<ul class="pagination pagination-sm" style="margin:0;"></ul>'+
				'</div>'+
				'<div name="jump-div" class="btn-group btn-group-sm hidden-xs" role="group">'+
					'<div class="input-group input-group-sm" style="width:120px;">'+
					  '<input name="jump" type="number" class="form-control" placeholder="page" min="1">'+
					  '<span class="input-group-btn">'+
						'<button name="jump-btn" class="btn btn-default" type="button">Go!</button>'+
					  '</span>'+
					'</div>'+
				'</div>' : null;
			
			
			// actions
			var actionsTpl = 
				'<div class="btn-group btn-group-sm" role="group" name="actions"></div>';
			
			$toolbar
				.append(
					pageLengthTpl,
					pageSelectorTpl,
					actionsTpl
				)
				.prependTo(this.$element);
			
			
			if(pageSelectorTpl){
				var $goto = $('[name="jump-div"]',$toolbar),
					fn = function(){
						var $input = $('input',$goto),
							pageIndex = parseInt($input.val()),
							min = parseInt($input.prop('min')),
							max = parseInt($input.prop('max'));
						if(isNaN(pageIndex) || pageIndex<min || (!isNaN(max) && pageIndex>max)){
							// invalid
							$input.val(min);
							pageIndex = 1;
						}
						self.moveToPage(pageIndex-1);
					};
				
				$goto
					.find('button')
					.click(fn);
				$('input',$goto).keypress(function (event) {
					var keycode = (event.keyCode ? event.keyCode : event.which);
					if (keycode == 13) {
						fn();
						return false;
					}
				});
			}
			
			if(pageLengthTpl){
				var pageLengthItems = [];
				
				itemsPerPage.forEach(function(item){
					pageLengthItems.push(
						$('<li>')
							.attr('value',item)
							.append('<a>'+item+'</a>')
							.click(function(){
								self.setItemsPerPage(item);
							})
					);
				});
			
				$('[name="page-length"]',this.$element)
					.find('ul')
					.append(pageLengthItems);
			}
			
		}
		
		
		// initialize the view
		this._view = (this.options.view instanceof View) ? this.options.view : new TableView(this.options.view);
		this._$view = $('<div class="view">').appendTo(this.$element);
		
		
		
		
		
		
		// init pagination
		if(this.options.pagination.enable){
			this._setItemsPerPage($.isArray(this.options.pagination.itemsPerPage) ? this.options.pagination.itemsPerPage[0] : this.options.pagination.itemsPerPage);
			this._index = 0;
		}
		
		
		if($.isFunction(this.options.before))
			this.options.before.call(self);
		
		// once the model is ready ...
		
		this._loader();
		
		$.when(
			this.model().init(self)
		).done(function(){
			
			// the model is ready now !
			
			
			
			if(self.options.sortBy){
				if(typeof self.options.sortBy == 'string')
					self.sort(self.options.sortBy,null,true);
				else
					self.sort(self.options.sortBy.field,self.options.sortBy.ascending,true);
			}
			
			// Initialize the view only after the model was initialized
			
			$.when( self.view().init(self._$view, self) ).done(function(){
				
				// load the data from the model
				self
					.open()
					.done(function(){
						
						if($.isFunction(self.options.loaded))
							self.options.loaded.call(self);
						
						setTimeout(function(){
							self.$element.trigger('load');
						},1);
					});
					
			});
		});
		
	}
	Table.prototype.model = function(){
		return this._model;
	}
	Table.prototype.view = function(){
		return this._view;
	}
	Table.prototype.items = function(){
		return this._items;
	}
	Table.prototype.selection = function(){
		var s = [];
		this._map.forEach(function(meta,i){
			if(meta.selected)
				s.push(this._items[i]);
		},this);
		return s;
	}
	Table.prototype._itemToIndex = function(item){
		var index;
		if(typeof item == 'function'){
			index = this._map.filter(function(meta,i){
				return item.call(this,this._items[i],meta.index);
			},this).map(function(meta){
				return meta.index;
			});
		}
		else if(Array.isArray(item)){
			index = item.map(function(e){
				return this.model().index(e);
			},this);
		}
		else if( typeof item != 'undefined')
			index = this.model().index(item);
		return index;
	}
	
	// index might be a function(item) -> return Boolean to select the elements that match some criteria
	// or an index used by the Model.index(item) function
	// returns true if there was a change
	Table.prototype.select = function(item){
		var selectable = this.options.selectable;
			
		if(!selectable.enable) return false;
		
		// remove previous selection
		this._select(this._itemToIndex(this.selection()), false, true);
		
		return this._select(this._itemToIndex(item) , true);
	}
	// index = model index !
	// table.selectByIndex(table.model().index(item)) <=> table.select(item)
	Table.prototype.selectByIndex = function(index){
		var selectable = this.options.selectable;
			
		if(!selectable.enable) return false;
		
		return this._select(index , true);
	}
	// the next function is for internal purpose only !
	// returns true only if there was a state change
	// index must be the one used by the model and stored in this._map[].index
	// if trigger == true, an event will be triggered on change only
	Table.prototype._select = function(index,state,notrigger){
		state = !!state;
		
		if($.isArray(index)){
			var change = false;
			index.forEach(function(si){
				if(this._select(si,state,true))
					change = true;
			},this);
			
			if(change && !notrigger)
				this.$element.trigger('selection.change');
			
			return change;
		}
		
		if(typeof index == 'undefined')
			return false;
		
		var i = this._indexToPosition(index),
			item = this._items[i],
			meta = this._map[i];
		
		// match the filter ?
		var filter = this.options.selectable.filter;
		if(i!=-1 && (!$.isFunction(filter) || filter.call(this,item,index))){
			
			var currentState = meta.selected;
			if(currentState != state){ // else nothing to do ! already in that state
				
				if(state){
					// check if the selection limit is reached
					var limit = this.options.selectable.limit;
					if(limit>0){
						var selectionLength = 0, firstSelectedIndex;
						this._map.forEach(function(meta,i){
							if(meta.selected){
								if(selectionLength==0)
									firstSelectedIndex = meta.index;
								selectionLength++;
							}
						},this);
						if(selectionLength >= limit){
							// limit reached
							if(limit>1)
								// do not check that item
								state = false;
							else
								// uncheck the previous one only if limit===1
								this._select(firstSelectedIndex,false);
						}
					}
				}
				
				// update the state
				meta.selected = state;
				
				// update the dom
				var $item = meta.$item;
				if(state)
					$item.addClass('selected');
				else
					$item.removeClass('selected');
				// update the view
				this.view().setSelectState($item,state);
				
				
				if(currentState != state){
					
					if(!notrigger)
						this.$element.trigger('selection.change');
					
					return true;
				}
			}
			
		}
		
		return false;
	}
	// internal use only, add ctr & shift feature on user selection
	Table.prototype._selectExtended = function(e,index,state){
		var i = this._indexToPosition(index),
			ctrlAndShiftSelectionEnable = !this.options.selectable.limit;
		
		// enable selecting multiple rows with the shift key
		if(e.shiftKey && ctrlAndShiftSelectionEnable){// to enable that feature, there must be no limit for the selection
			
			var selection = this._map.filter(function(meta){
				return meta.selected;
			});
			
			if(selection.length>0){
				var positionEnd = i,
					positionStart = this._indexToPosition(selection.length>1 ? this._selectSrc : selection[0].index);
				
				if(positionStart>positionEnd){
					positionEnd = positionStart;
					positionStart = i
				}
				
				this._select(this._map.filter(function(m,i){
					return i>=positionStart && i<=positionEnd;
				}).map(function(m){
					return m.index;
				}),true);
				
				this._selectType = 'shift';
				
				return;
			}
			
		}
		
		if(!this.options.selectable.cumul && !(e.ctrlKey && ctrlAndShiftSelectionEnable)){
			// remove previous selection
			this._select(this._map.filter(function(meta){
				return meta.selected;
			}).map(function(m){
				return m.index;
			}),false,true);
		}
		
		this._selectSrc = index;
		this._select(index,state);
	}
	Table.prototype.open = function(parent){
		
		var model = this.model(),
			view = this.view(),
			self = this;
		
		this._parent = parent || null;
		
		// reset the items
		var hasItemSelected = this.selection().length;
		this._items = [];
		this._map = [];
		if(hasItemSelected)
			this.$element.trigger('selection.change'); // the selection was lost
		
		
		this._loader();
		
		return $.when( model.data(this._parent, this._index, this._itemsPerPage) )
			.done(function(items){
				
				self._items = items || [];
				
				// pagination : if we do not know the total number of rows, ask the model !
				if(self.options.pagination.enable && !self._length){
					self._length = model.rows();
					self._updatePagination();
				}
				
				self._loader(false);
				
				self._update();
				
			})
			.fail(function(e){
				
				self._message(typeof self.options.message.modelLoadError == 'function' ? self.options.message.modelLoadError.call(self,e) : self.options.message.modelLoadError);
				
				if(typeof self.options.error == 'function')
					self.options.error.apply(self,arguments);
			})
		
	}
	Table.prototype._indexToPosition = function(index){
		for(var i=0; i<this._map.length; i++)
			if(this._map[i].index === index)
				return i;
	}
	Table.prototype._loader = function(enable){
		this._message(enable===false ? null : (typeof this.options.message.loading == 'function' ? this.options.message.loading.call(this) : this.options.message.loading));
	}
	Table.prototype._message = function(message){
		if(message===null){
			if(this._$notify)
				this._$notify.hide();
			this._$view.show();
		}
		else {
			if(!this._$notify){
				this._$notify = $('<div>').addClass('tbl-notify');
				this._$view.after(this._$notify);
			}
			this._$notify.html(message).show();
			this._$view.hide();
		}
	}
	Table.prototype._update = function(){
		
		var rowClass = (this.options.row || {}).class,
			rowEvents = (this.options.row || {}).events,
			selectable = this.options.selectable || {},
			selectOnClick = (typeof selectable.trigger == 'string' && selectable.trigger.indexOf('click')>=0),
			openable = this.options.openable || {},
			model = this.model(),
			view = this.view(),
			self = this;
		
		view.clear();
		
		this._map = []; // it map some state/relation information to the index
		/*
		{
			$item: jquery dom element (from the view)
			index: can be anything, given by the Model.index() function, but is unique in the items collection
			selected: boolean
		}
		*/
		
		if(this._items.length==0){
			this._message(typeof this.options.message.empty == 'function' ? this.options.message.empty.call(this) : this.options.message.empty);
			return;
		}
		
		this._items.forEach(function(item,i){
			
			var index = model.index(item);
			
			// create the item in the view
			var $tr = view.createItem(item, index);
			
			$tr.attr('data-role','item');
			$tr.addClass(rowClass);
			
			if(index===null)
				index = i; // if the modal have no index, a default one is given corresponding of the position of the item in the collection
			
			this._map.push({
				$item: $tr,
				index: index,
				selected: false
			});
			
			// user events (first so the user event can cancel default event)
			for(var event in rowEvents)
				$tr.on( event , {
					item: item,
					index: index
				}, rowEvents[event] );
			
			// selection
			if(selectable.enable){
				var itemSelectable = $.isFunction(selectable.filter) ? selectable.filter.call(this,item,index) : true;
				if(selectOnClick && itemSelectable)
					$tr.on( 'click' , function(e){
						self._selectExtended(e,self._map[i].index,!self._map[i].selected); // toggle
					});
			}
			
			// openable ?
			if(openable.enable && model.hasChildren(item)){
				$tr.on( openable.trigger , function(){
						self.open(item);
					});
			}
			
			
			
			
			
			// data
			$tr.data('table',this);
			$tr.data('item',item);
			
			
		},this);
		
		this.$element.trigger('redraw');
		
	}
	
	Table.prototype.destroy = function(){
		this.$element.empty().removeClass('tbl').removeClass(this.options.class);
		
		this.$element.trigger('destroy');
	}
	// if sens==true, ascending order, else descending order
	// if sens is ommited, then its default value is true (ascending order)
	// if sens is ommited and field start with '+', then the sort will be in ascending order (ie: +field)
	// if sens is ommited and field start with '-', then the sort will be in descending order (ie: -field)
	Table.prototype.sort = function(field, sens, __noUpdate){ // the third parameter is for internal use only
		if(typeof field != 'string' || !/^[+-]?.+$/.test(field))
			return;
		
		if(typeof sens == 'undefined' || sens === null)
			sens = !/^\-/.test(field);
		
		field = field.replace(/^[+-]?/,'');
		
		
		this._sortedBy = (sens ? '+' : '-') + field;
		this.model().sort(field,sens);
		if(__noUpdate!==true)
			this.open(this._parent);

	}
	Table.prototype.sortedBy = function(){
		return this._sortedBy;
	}
	Table.prototype.reload = function(){
		return this.open(this._parent);
	}
	
	// pagination
	
	// pageIndex starts from 0
	// pageIndex === '+1' -> go to next page
	// pageIndex === '-1' -> go to previous page
	Table.prototype.moveToPage = function(pageIndex){
		var self = this;
		if(this.options.pagination.enable){
			
			if(typeof pageIndex == 'string'){
				var currentPage = Math.floor((this._index || 0) / this._itemsPerPage);
				currentPage += parseInt(pageIndex);
				return this.moveToPage(currentPage);
			}
			
			if(pageIndex<0)
				pageIndex = 0;
			
			this._index = (pageIndex || 0 )* this._itemsPerPage;
			
			this._updatePagination();
			
			// reload !
			this.open(this._parent);
			
		}
	}
	Table.prototype.setItemsPerPage = function(itemsPerPage){
		if(this.options.pagination.enable){
			
			this._setItemsPerPage(itemsPerPage);
			
			// reload
			this.moveToPage(0);
			
		}
	}
	Table.prototype._setItemsPerPage = function(itemsPerPage){
		
		if(typeof itemsPerPage == 'string' && /^all$/i.test(itemsPerPage))
			this._itemsPerPage = null;
		else if(typeof itemsPerPage == 'number' && itemsPerPage>0)
			this._itemsPerPage = itemsPerPage;
		
		var $epp = $('[name="page-length"]',this.$element);
		
		$epp.find('.value').html(itemsPerPage);
		
		$epp
			.find('li')
			.removeClass('selected')
			.filter('[value="'+(this._itemsPerPage || 'all')+'"]')
			.addClass('selected');
	}
	Table.prototype.numberOfPage = function(){
		return (this.options.pagination.enable && this._itemsPerPage !== null) ? (this._length>0 ? Math.ceil(this._length/this._itemsPerPage) : null) : 1;
	}
	Table.prototype.currentPage = function(){
		return this._itemsPerPage ? Math.floor(this._index / this._itemsPerPage) : 0;
	}
	// internal use only 
	Table.prototype._updatePagination = function(){
		if(this.options.pagination.enable){
			
			// update the toolbar
			
			var self = this,
				nbPage = this.numberOfPage(),
				currentPage = this.currentPage(); // start from 0
			
			var $goto = $('[name="jump-div"]',this.$element),
				$navigator = $('[name="pagination-div"]',this.$element);
			
			if(nbPage===1){
				// only one page ! so do not show the pagination controls
				$goto.hide();
				$navigator.hide();
			}
			else {
			
				if(nbPage) // the number of page is known
					$goto
						.find('input')
						.attr('max',nbPage);
				else
					$goto
						.find('input')
						.removeAttr('max');
				
				
				var $ul = $navigator
					.find('ul')
					.empty();
				
				var hasNext = !nbPage || (currentPage+1 < nbPage),
					hasPrev = (currentPage > 0),
					maxItem = 3; // must be odd
					
				if(hasPrev)
					$('<a aria-label="Previous"><span aria-hidden="true">&laquo;</span></a>')
						.click(function(){
							self.moveToPage('-1');
						})
						.appendTo($ul)
						.wrap('<li>');
				
				var nbNext = nbPage ? (nbPage - 1 - currentPage) : 0,
					half = Math.floor(maxItem/2),
					decal = nbNext >= half ? 0 : (nbNext-half),
					pageIndex = currentPage /*+ 1*/, // start from 1
					indexes = [];
				for(var i=-half+decal+pageIndex, j=0; j<maxItem && i<=(nbPage?(nbPage-1):pageIndex); i++){
					if(i>=0){
						indexes.push(i);
						j++;
					}
				}
				indexes.forEach(function(i){
					$('<a>'+(i+1)+'</a>')
						.click(function(){
							self.moveToPage(i);
						})
						.appendTo($ul)
						.wrap('<li '+(pageIndex==i?'class="active"':'')+'>');
				},this);
				
				if(hasNext)
					$('<a aria-label="Next"><span aria-hidden="true">&raquo;</span></a>')
						.click(function(){
							self.moveToPage('+1');
						})
						.appendTo($ul)
						.wrap('<li>');
				
				

				// show pagination's controls
				$goto.show();
				$navigator.show();
			
			}
			
			
		}
		
	}
	
	
	
	
	
	
	
	/*
	  Model interface
	*/
	
	var Model = function() {}
	// init the model, may return a deferred object for asynchronous init model, or nothing else
	// override this for asynchronous model initialization
	Model.prototype.init = function(tableInstance){}
	// return the keys/columns
	Model.prototype.keys = function(){
		return [];
	}
	// return the number of rows, null if not known
	Model.prototype.rows = function(){
		return null;
	}
	// return the items
	// offset and length are used for pagination
	// may return a jquery deferred object if the processus is asynchronous
	Model.prototype.data = function(parent, offset, length){
		// parent is null if root
		// an item must be an object
		// the property '__index' must be set with a unique identifier representing the item (for table model, it can be an integer index)
		return [];
	}
	// check if an item has children or not (tree model may have)
	Model.prototype.hasChildren = function(item){
		return false;
	}
	// sort the data
	Model.prototype.sort = function(field, ascending){}
	// return a unique index identifying an items according to the data given in argument
	// if null returned, a default index will be assigned corresponding to the position of the item in the collection
	Model.prototype.index = function(item){
		return null;
	}
	
	
	Table.Model = Model;
	
	
	
	/*
	ArrayModel
	*/
	
	// items must be an array or a jquery deferred object !
	var ArrayModel = function(items) {
		
		var self = this,
			setData = function(data){
				self._items = Array.isArray(data) ? data : [];
				self._type = self._items.length ? (typeof self._items[0]) : 'undefined';
				if(self._type == 'undefined')
					self._items = []; // make an array of undefined unvalid
			};
		
		setData(items);
		
		
		// deferred object given ?
		this._deferred = null;
		if(typeof items == 'object' && !Array.isArray(items)){
			this._deferred = items;
			this._deferred.done(setData);
		}
		
		
		Model.call(this);
	}
	ArrayModel.prototype = Object.create(Model.prototype);
	
	// execute the callback when the model is ready (ie: the keys are known)
	ArrayModel.prototype.init = function(){
		return this._deferred ? this._deferred : null;
	}
	
	// return the keys/columns
	ArrayModel.prototype.keys = function(){
		switch(this._type){
			case 'object':
				return Object.keys(this._items[0]).filter(function(k){
					return !/^__/.test(k); // skip the key starting with '__' (double underscores)
				});
			case 'number':
			case 'function':
			case 'boolean':
			case 'string':
				return ['value'];
			default:
				return [];
		}
	}
	// return the number of rows, null if not known
	ArrayModel.prototype.rows = function(){
		return this._items.length;
	}
	// return the items
	// offset and length are used for pagination
	ArrayModel.prototype.data = function(parent, offset, length){
		// parent is null if root
		// an item must be an object
		// the property '__index' may be set with a unique identifier representing the item (for table model, it can be an integer index)
		offset = offset||0;
		return length ? this._items.slice(offset,offset+length) : this._items.slice(offset);
	}
	// sort the data
	ArrayModel.prototype.sort = function(field, ascending){
		if(this._type == 'object')
			this._items.sort(function(a, b){
				a = typeof a.field == 'function' ? a.field() : a.field;
				b = typeof b.field == 'function' ? b.field() : b.field;
				if(a < b) return -1;
				if(a > b) return 1;
				return 0;
			});
		else if(this._type == 'function')
			this._items.sort(function(a, b){
				a = a();
				b = b();
				if(a < b) return -1;
				if(a > b) return 1;
				return 0;
			});
		else
			this._items.sort();
		
		if(!ascending)
			this._items.reverse();
	}
	// return a unique index identifying an items according to the item given in argument
	ArrayModel.prototype.index = function(item){
		return this._items.indexOf(item);
	}
	
	
	Table.ArrayModel = ArrayModel;
	
	
	
	
	/*
	* View
	*/
	var View = function() {}
	// init the view, may return a deferred object for asynchronous init view, or nothing else
	// the first parameter is the container (jQuery object) where to build the view
	// table : the parent table
	View.prototype.init = function($container, table){
		// the next line is important if you do not override the View.prototype.$ function.
		this.$ = function(){
			return $($container);
		};
		this.table = function(){
			return table;
		};
	}
	// clear all items in the view
	View.prototype.clear = function(){}
	// create a new item into the view
	View.prototype.createItem = function(item,index){}
	// update the select state of an item
	View.prototype.setSelectState = function($item, checked){}
	
	
	Table.View = View;
	
	
	
	var TableView = function(opt) {
		
		View.call(this);
		
		this.options = $.extend(true,{
			header: {
				enable: true // make the header visible or not !
			},
			selectable: {
				check: false // enable selecting rows with a checkbox
			},
			fields: {}, // field option, see below for details
			showOnlySpecifiedField: false // if set, only the fields set in 'fields' will be show (ie: white list)
		},opt);
		
		this._fields = {};
		
		
	}
	TableView.prototype = Object.create(View.prototype);
	
	TableView.prototype.init = function($container, table){
		
		View.prototype.init.call(this,$container,table);
		
		// checkable column
		var selectable = table.options.selectable;
		if(selectable.enable && this.options.selectable.check){
			// prepend a special field '__check'
			this._fields['__check'] = {
				label:'',
				get: function(item,index){
					var itemSelectable = $.isFunction(selectable.filter) ? selectable.filter.call(table,item) : true;
					if(itemSelectable){
						// check for a limitation
						return $('<input type="checkbox" data-role="select"/>').on('change',function(e){
							// on checkbox change
							table._selectExtended(e,index,$(this).prop("checked"));
							// do not fire the row's click event
							e.preventDefault();
							return false;
						});
					}
					return null;
				}
			};
		}
		
		
		/*
		fields management (the model must be ready !)
		*/
		
		$.extend(true,this._fields,this.options.fields);
		
		// set default fields
		if(!this.options.showOnlySpecifiedField)
			table.model().keys().forEach(function(field){
				if(!this._fields.hasOwnProperty(field))
					this._fields[field] = {};// defaults will be set just below
			},this);
		for(var i in this._fields){
			this._fields[i] = $.extend({
				label: i, // displayed name of that field
				get: null, // function(item) -> return value
				formatter: null, // function(value) -> return String
				enable: true, // show/hide this field
				default: null, // default value
				class : null, // className(s) to be added to the td/th DOM element for this field, multiple classname must be separated by space
				hidden: false,
				event: null // object, used to attach event on a TD dom element
			},this._fields[i]);
		}
		
		
		/*
		* DOM
		*/
		
		$container.addClass('tableview');
		
		var fields = this._fields, self = this;
		
		this._$table = $('<table><tbody>').appendTo($container);
		this._$tbody = $('tbody',this._$table);
		
		// set the index, internal usage only, todo : make it private ? (used in setVisible())
		this._index = {};
		var coln = 0;
		$.each(fields,function(field,fieldOptions){
			if(fieldOptions.enable)
				self._index[field] = coln++;
		});
		
		var sortedBy = table.sortedBy(), sortField, sortSens;
		if(sortedBy){
			sortField = sortedBy.replace(/^[-+]?/,'');
			sortSens = !/^\-/.test(sortedBy);
		}
		
		// update the DOM header element
		$('thead',this._$table).remove();
		if(this.options.header.enable){
			var $thead = $('<thead>').prependTo(this._$table),
				$tr = $('<tr>');
			
			$.each(fields,function(field,fieldOptions){
				if(fieldOptions.enable){
					var $th = $('<th>');
					$th
						.html(fieldOptions.label)
						.addClass(fieldOptions.class);
					
					if(field!="__check"){ // make all the field sortable except the special '__check' field 
						$th
							.addClass('sortable')
							.on('click',function(){
								var $this = $(this),
									ascending = !Boolean($this.data('ascending'));
								$this.data('ascending',ascending);
								table.sort(field,ascending);
								
								// update the header
								$('th',$thead).each(function(){
									var $this = $(this);
									$this
										.removeClass('sort-asc sort-desc');
								});
								
								$this.addClass(ascending ? 'sort-asc' : 'sort-desc');
							});
						
						if(sortField === field)
							$th.addClass(sortSens ? 'sort-asc' : 'sort-desc');
					}
					
					if(fieldOptions.hidden)
						$th[0].style.display = "none";
					
					$th.data('field',field);
					
					$tr.append($th);
				}
			});
			
			$tr.appendTo($thead);
			
		}
	}
	TableView.prototype.clear = function(){
		this._$tbody.empty();
	}
	TableView.prototype.createItem = function(item,index){
		// construct the item dom element
		var $tr = $('<tr>');
		
		for(var field in this._fields){
			var fieldOptions = this._fields[field];
			if(fieldOptions.enable){
				var value = $.isFunction(fieldOptions.get) ? fieldOptions.get.call(this,item,index) : (
						(typeof item[field] != 'undefined') ? 
						($.isFunction(item[field]) ? item[field]() : item[field])
						: (fieldOptions.default===null ? "" : fieldOptions.default)
					);
				
				if($.isFunction(fieldOptions.formatter))
					value = fieldOptions.formatter.call(this,value);
				
				
				var $td = $('<td>');
				
				$td
					.html( value )
					.addClass(fieldOptions.class);
				
				if(fieldOptions.hidden)
					$td[0].style.display = "none";
				
				if(typeof fieldOptions.events == 'object')
					for(var eventName in fieldOptions.events){
						$td.on(eventName,{
							item: item
						},fieldOptions.events[eventName]);
					}
				
				$tr.append($td);
			}
		}
		
		this._$tbody.append($tr);
		
		return $tr;
	}
	TableView.prototype.setSelectState = function($item, checked){
		// check the checkbox (if any)?
		$('input[data-role="select"]',$item)
			.prop("checked",checked);
	}
	TableView.prototype.setVisible = function(field, show){
		if(this._fields.hasOwnProperty(field) && this._fields[field].enable){
			// update the view
			// get the index of the column
			var index = this._index[field] + 1; // start from 1
			// hide/show it !
			var $col = $("thead tr th:nth-child("+index+"), tbody tr td:nth-child("+index+")",this._$table);
			$col.toggle(Boolean(show));
			
			// save the state
			this._fields[field].hidden = !show;
		}
	}
	TableView.prototype.hide = function(field){
		this.setVisible(field,false);
	}
	TableView.prototype.show = function(field){
		this.setVisible(field,true);
	}
	TableView.prototype.isVisible = function(field){
		return this._fields.hasOwnProperty(field) && this._fields[field].enable && !this._fields[field].hidden;
	}
	
	
	Table.TableView = TableView;
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery)
		window.jQuery.addPlugin('Table',Table);
	

})();
