(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    } else {
        // Browser globals
        root.Table = factory(root.jQuery);
    }
}(this, function ($) {
	
	
	var isTouchDevice = navigator ? (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase())) : false;
	
	
	/*
	events :
		- "selection.change" // is fired each time the selection change, (note: the selection is cleared when the page change or the data is reloaded
	*/
	
	var Table = function(element,opt){
		
		this.$element = $(element);
		this.options = $.extend(true,{
			model: null, // Model instance or array (will be converted into an ArrayModel, can be an URL pointing to JSON data)
			view: null, // View instance or options for the TableView 
			selectable: {
				enable: false, // enable selecting
				limit: 0, // limit the selection to a specific number, if 0 or null -> unlimited (for activating shift & ctrl selection, limit must be 0 or null)
				filter: null, // function(item) -> return boolean , if it returns false, this item is not selectable
				trigger: 'click', // the event name to be triggered on the selected row. If you want the selection to be effective only on a limited portion of the row, pass an object such as { event: 'click', selector: 'col-icon' }
				cumul: true, // if true the selection is always cumulative, else the selection is reset at every new selection
				callback: null
			},
			openable:{
				enable: true, // if the item has has children, open that children
				trigger: isTouchDevice ? 'click' : 'dblclick', // click or dblclick or any jquery event that are available on <tr> item. If you want the open behaviour to be effective only on a limited portion of the row, pass an object such as { event: 'click', selector: 'col-icon' }
				open: null // function, fired when the user try to open an item that does not have any children
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
				itemsPerPage: 20, // may be a number, 'all', an array of available values [20,50,100,'all'], or 'lazy' for enabling lazy loading
				enable: false, // enable the pagination
				lazyLoadingItemsPerRequest: 40, // how much items to load on every request
				lazyScrollTarget: null, // on which element to listen to the scroll event, default to element
				lazyOffset: 100 // number of pixel from the bottom when the new set of data must be loaded
			},
			sortBy: null, // can either be a string (ie: "+field" or "-field" or "field") or an object { field: "field", ascending: true|false }
			message: {
				empty: '<span class="tbl-message-warning">empty</span>',
				modelLoadError: '<span class="tbl-message-warning">error</span>',
				loading: '<span class="tbl-message-warning">loading...</span>'
			}
		},opt);
		
		
		if(!this.options.pagination.lazyScrollTarget)
			this.options.pagination.lazyScrollTarget = element;
		
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
		var hasToolbar = this.options.pagination.enable; // why not always true ?
		if(hasToolbar){
			var $toolbar = $('<div class="tbl-toolbar toolbar btn-toolbar" role="toolbar">');
				
			// page length
			var itemsPerPage = this.options.pagination.itemsPerPage;
			if(!$.isArray(itemsPerPage) && itemsPerPage!=='lazy')
				itemsPerPage = [itemsPerPage];
			var lazyLoading = itemsPerPage==='lazy';
			var pageLengthTpl = (this.options.pagination.enable && !lazyLoading && itemsPerPage.length>1) ?
				'<div class="btn-group btn-group-sm" role="group" name="page-length">'+
					'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'+
						'<span><span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span> <span class="value"></span></span>'+
					  '</button>'+
					 '<ul class="dropdown-menu"></ul>'+
				'</div>' : null;
			
			// pagination + go to page N
			var pageSelectorTpl = this.options.pagination.enable && !lazyLoading ?
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
			
			if(this.options.pagination.itemsPerPage==='lazy'){
				$(this.options.pagination.lazyScrollTarget).on('scroll.table', function(){
					self._updatePagination();
				});
			}
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
					.open(null, true)
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
	Table.prototype.next = function(item){
		for(var i=0; i<this._items.length; i++)
			if(this._items[i] === item)
				return this._items[i+1];
	}
	Table.prototype.prev = function(item){
		for(var i=0; i<this._items.length; i++)
			if(this._items[i] === item)
				return this._items[i-1];
	}
	Table.prototype.first = function(){
		return this._items[0];
	}
	Table.prototype.last = function(){
		return this._items[this._items.length-1];
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
	Table.prototype.select = function(item, append){
		return this.selectByIndex(this._itemToIndex(item) , append);
	}
	// index = model index !
	// table.selectByIndex(table.model().index(item)) <=> table.select(item)
	Table.prototype.selectByIndex = function(index, append){
		var selectable = this.options.selectable;
			
		if(!selectable.enable) return false;
		
		// remove previous selection
		var forceTrigger = false;
		if(!append)
			forceTrigger = this._select(this._itemToIndex(this.selection()), false, true);
		
		if(!this._select(index , true) && forceTrigger){
			this.$element.trigger('selection.change');
		}
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
		
		if(typeof index == 'undefined'){
			return false;
		}
		
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
				this.view().setSelectState(item, state, $item);
				
				
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
	
	Table.prototype._selectExtended = function(evt,index,state){
		var self = this;
		
		function resetSelection(){
			// remove previous selection
			self._select(self._map.filter(function(meta){
				return meta.selected;
			}).map(function(m){
				return m.index;
			}),false,true);
		};
		
		if(evt.shiftKey){
			
			var selectionBoundaries = [null,null],
				i = this._indexToPosition(index);
			
			this._map.forEach(function(meta, index){
				if(meta.selected && selectionBoundaries[0]===null){
					selectionBoundaries[0] = index;
				}
				if(meta.selected && selectionBoundaries[0]!==null){
					selectionBoundaries[1] = index;
				}
			});
			
			var newSelection = [];
			
			if(this.options.selectable.cumul){
				for(var j=Math.min(i,selectionBoundaries[0]); j<=Math.max(i,selectionBoundaries[1]); j++){
					newSelection.push(this._map[j].index);
				}
			} else {
				// remove previous selection
				resetSelection();
				
				for(var j=(i<selectionBoundaries[0] ? i : selectionBoundaries[0]); j<=(i<selectionBoundaries[0] ? selectionBoundaries[0] : i); j++){
					newSelection.push(this._map[j].index);
				}
			}
			
			
			this._select(newSelection, true);
			
		} else if(this.options.selectable.cumul || evt.ctrlKey){
			this._select(index, state);
		} else {
			resetSelection();
			this._select(index, true);
		}
	}
	
	/*
	 reset : only available for lazyloading mode. For internal purpose only.
	*/
	Table.prototype.open = function(parent, reset){
		
		var model = this.model(),
			view = this.view(),
			self = this,
			lazyLoading = this.options.pagination.enable && this.options.pagination.itemsPerPage === 'lazy',
			selection = null;
		
		this._parent = parent || null;
		
		if(reset===true || !lazyLoading){
			// reset the items
			selection = this.selection();
			this._items = [];
			this._map = [];
			if(selection.length)
				this.$element.trigger('selection.change'); // the selection was lost
			
			if(lazyLoading) this._index = 0;
			
			this._loader();
		}
		
		this._loadingData = true;
		
		var itemsPerPage = this._itemsPerPage;
		return $.when( model.data(this._parent, this._index, itemsPerPage) )
			.always(function(){
				delete self._loadingData;
			})
			.done(function(items){
				
				items = items || [];
				
				self._items = self._items.concat(items);
				
				self._endReached = items.length < itemsPerPage;
				
				// pagination : if we do not know the total number of rows, ask the model !
				if(self.options.pagination.enable && !self._length){
					self._length = model.rows();
					self._updatePagination();
				}
				
				self._loader(false);
				
				self._update(reset);
				
				if(selection && selection.length)
					self.select(selection);
				
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
		return -1;
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
	Table.prototype._update = function(reset){
		
		var rowClass = (this.options.row || {}).class,
			rowEvents = (this.options.row || {}).events,
			selectable = this.options.selectable || {},
			openable = this.options.openable || {},
			model = this.model(),
			view = this.view(),
			self = this,
			lazyLoading = this.options.pagination.enable && this.options.pagination.itemsPerPage === 'lazy';
		
		var selectTriggers = Array.isArray(selectable.trigger) ? selectable.trigger : (selectable.trigger ? [selectable.trigger] : []);
		for(var i=0; i<selectTriggers.length; i++){
			if(typeof selectTriggers[i] === 'string')
				selectTriggers[i] = { event: selectTriggers[i] };
		}
		
		var openableTriggers = Array.isArray(openable.trigger) ? openable.trigger : (openable.trigger? [openable.trigger] : []);
		for(var i=0; i<openableTriggers.length; i++){
			if(typeof openableTriggers[i] === 'string')
				openableTriggers[i] = { event: openableTriggers[i] };
		}
		
		
		if(!lazyLoading || reset===true){
			view.clear();
		
			this._map = []; // it map some state/relation information to the index
			/*
			{
				$item: jquery dom element (from the view)
				index: can be anything, given by the Model.index() function, but is unique in the items collection
				selected: boolean
			}
			*/
		
		}
		
		if(this._items.length==0){
			this._message(typeof this.options.message.empty == 'function' ? this.options.message.empty.call(this) : this.options.message.empty);
			return;
		}
		
		var startIndex = this._map.length;
		
		this._items.forEach(function(item,i){
			
			if(i<startIndex) return; // used for lazyLoading
			
			var index = model.index(item);
			
			// create the item in the view
			var $tr = view.createItem(item, index);
			
			$tr.attr('data-role','item');
			$tr.addClass(rowClass);
			
			if(index===null)
				index = i; // if the model have no index, a default one is given corresponding of the position of the item in the collection
			
			this._map.push({
				$item: $tr,
				index: index,
				selected: false
			});
			
			// user events (first so the user event can cancel default event)
			for(var event in rowEvents)
				$tr.on( event , {
					item: item,
					index: index,
					$item: $tr
				}, rowEvents[event] );
			
			// selection
			if(selectable.enable && selectTriggers.length){
				var itemSelectable = $.isFunction(selectable.filter) ? selectable.filter.call(this,item,index,$tr) : true;
				if(itemSelectable){
					selectTriggers.forEach(function(selectTrigger){
						$tr.on( selectTrigger.event , selectTrigger.selector, function(evt){
							evt.stopImmediatePropagation();
							
							var selected = !self._map[i].selected;
							
							if(typeof selectable.callback === 'function'){
								var res = selectable.callback.call(self,item,index,selected,$tr);
								if(typeof res === 'boolean'){
									selected = res;
								}
							}
							
							self._selectExtended(evt,self._map[i].index,selected); // toggle
						});
					})
				}
			}
			
			// openable ?
			if(openable.enable && openableTriggers.length){
				openableTriggers.forEach(function(openableTrigger){
					$tr.on( openableTrigger.event, openableTrigger.selector , function(evt){
						
						var prevent = false;
						
						if(typeof openable.open == 'function' && openable.open.call(self, item, index, $tr)===false)
							prevent = true;
						
						if(!prevent && model.hasChildren(item))
							self.open(item, true);
						
						evt.stopImmediatePropagation();
					});
				})
			}
			
			
			
			
			
			// data
			$tr.data('table',this);
			$tr.data('item',item);
			
			
		},this);
		
		this.$element.trigger('redraw');
		
	}
	
	Table.prototype.destroy = function(){
		
		this.view().clear();
		
		if(this.options.pagination.enable && this.options.pagination.itemsPerPage === 'lazy')
			$(this.options.pagination.lazyScrollTarget).off('scroll.table');
		
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
			this.open(this._parent, true);

	}
	Table.prototype.sortedBy = function(){
		return this._sortedBy;
	}
	Table.prototype.reload = function(){
		return this.open(this._parent, true);
	}
	
	// pagination
	
	// pageIndex starts from 0
	// pageIndex === '+1' -> go to next page
	// pageIndex === '-1' -> go to previous page
	Table.prototype.moveToPage = function(pageIndex){
		var self = this;
		if(this.options.pagination.enable){
			
			if(typeof pageIndex == 'string'){
				var currentPage = this.currentPage();
				currentPage += parseInt(pageIndex);
				return this.moveToPage(currentPage);
			}
			
			if(pageIndex<0)
				pageIndex = 0;
			
			var index = (pageIndex || 0 )* this._itemsPerPage;
			
			if(this._endReached) return;
			if(typeof this._length === 'number' && this._length >=0 && index>=this._length) return;
			
			this._index = index;
			
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
		else if(typeof itemsPerPage == 'string' && /^lazy$/i.test(itemsPerPage))
			this._itemsPerPage = this.options.pagination.lazyLoadingItemsPerRequest;
		else if(typeof itemsPerPage == 'number' && itemsPerPage>0)
			this._itemsPerPage = itemsPerPage;
		else
			return; // invalid
		
		var $epp = $('[name="page-length"]',this.$element);
		
		$epp.find('.value').html(itemsPerPage);
		
		$epp
			.find('li')
			.removeClass('selected')
			.filter('[value="'+String(itemsPerPage)+'"]')
			.addClass('selected');
	}
	Table.prototype.numberOfPage = function(){
		return (this.options.pagination.enable && typeof this._itemsPerPage === 'number') ? (this._length && this._length>0 && this._itemsPerPage ? Math.ceil(this._length/this._itemsPerPage) : null) : 1;
	}
	Table.prototype.currentPage = function(){
		return this._itemsPerPage ? Math.floor((this._index || 0) / this._itemsPerPage) : 0;
	}
	// internal use only 
	Table.prototype._updatePagination = function(){
		if(this.options.pagination.enable){
			
			if(this.options.pagination.itemsPerPage !== 'lazy'){
			
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
			
			} else {
				
				if(this._loadingData){
					return;
				}
				
				var target = this.options.pagination.lazyScrollTarget;
				var offset = this.options.pagination.lazyOffset;
				var $target = $(target);
				var totalHeight = target === window ? $(document).height() : $target[0].scrollHeight;
				var bottom = totalHeight - ($target.scrollTop()+$target.height());
				var atBottom = bottom <= offset;
				
				if(this._lazyLastBottom === bottom){
					return; // avoid infinite loop, no change
				}
				this._lazyLastBottom = bottom;
				
				if(atBottom){
					this.moveToPage('+1');
				}
				
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
	View.prototype.clear = function(){
		
	}
	// create a new item into the view
	View.prototype.createItem = function(item,index){}
	// update the select state of an item
	View.prototype.setSelectState = function(item, checked, $item){}
	
	
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
			showOnlySpecifiedField: false, // if set, only the fields set in 'fields' will be show (ie: white list)
			class: null
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
				class: '__select',
				get: function(item,index){
					var itemSelectable = $.isFunction(selectable.filter) ? selectable.filter.call(table,item) : true;
					if(itemSelectable){
						return $('<input type="checkbox" data-role="select"/>').on('click',function(evt){
							
							var selected = $(this).prop("checked");
						
							if(typeof selectable.callback === 'function'){
								var res = selectable.callback.call(self,item,index,selected);
								if(typeof res === 'boolean'){
									selected = res;
								}
							}
							
							// on checkbox change
							table._selectExtended(evt,index,selected);
							
						});
					}
					return null;
				},
				sortable: false
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
			if(!$.isPlainObject(this._fields[i])){
				delete this._fields[i];
				continue;
			}
			this._fields[i] = $.extend({
				label: i, // displayed name of that field
				get: null, // function(item) -> return value
				formatter: null, // function(value) -> return String
				enable: true, // show/hide this field
				default: null, // default value
				class : null, // className(s) to be added to the td/th DOM element for this field, multiple classname must be separated by space
				hidden: false,
				event: null, // object, used to attach event on a TD dom element
				sortable: true
			},this._fields[i]);
		}
		
		
		/*
		* DOM
		*/
		
		$container.addClass('tableview');
		
		var fields = this._fields, self = this;
		
		this._$table = $('<table><tbody>').appendTo($container).addClass(this.options.class);
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
					
					if(field!="__check" && fieldOptions.sortable){ // make all the field sortable except the special '__check' field 
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
				var value = $.isFunction(fieldOptions.get) ? fieldOptions.get.call(this,item,index,$tr) : (
						(typeof item[field] != 'undefined') ? 
						($.isFunction(item[field]) ? item[field]() : item[field])
						: (fieldOptions.default===null ? "" : fieldOptions.default)
					);
				
				if($.isFunction(fieldOptions.formatter))
					value = fieldOptions.formatter.call(this,value);
				
				
				var $td = $('<td>');
				
				$td
					.html( typeof value == 'object' ? value : value.toString() )
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
	TableView.prototype.setSelectState = function(item, checked, $item){
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
	
	$.Table = Table;
	
	$.fn.table = function(){
		var args = [].slice.call(arguments);
		
		if (this[0]) { // this[0] is the renderTo div
			
			var instance = $(this[0]).data('table');
			
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
			instance = new Table(this[0],args[0],args[1],args[2],args[3],args[4],args[5],args[6]);
			$(this[0]).data('table',instance);
			
			return this;
		}
	};
	
	
	return Table;
	

}));
