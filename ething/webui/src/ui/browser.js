(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'table', 'ething', 'ui/utils', 'ui/meta', 'css!font-awesome', 'css!ui/browser'], factory);
    }
}(this, function ($, Table, EThing, UI, Meta) {
	
	
	function inherits(extended, parent){
		extended.prototype = Object.create(parent.prototype);
	};
	
	
	
	/*
	* Browser
	*/
	
	function generateSvgResourceIcon(resource, square, style){
		var content = null, type = typeof resource == 'string' ? resource : resource.baseType();
		
		content = Meta.get(resource, 'icon')();
		
		if(!content){
			if(type==='Select'){
				content = '<path d="M 6 14 L 15 22 L 26 8"  stroke-width="2"/>';
			} else {
				content = '<text x="16" y="24" font-size="22" font-weight="bold" font-family="Arial" text-anchor="middle">?</text>';
			}
		}
		
		return '<svg class="icon-'+type+'" '+(style ? 'style="'+style+'"' : '')+' viewBox="0 0 32 32">'+(square ? '<rect x="0" y="0" width="32" height="32"/>' : '<circle cx="16" cy="16" r="16" />')+content+'</svg>';
	}
	
	
	
	
	function Browser(dom,opt){
		
		var options = $.extend(true,{
			model:null, // will be set after
			// table options
			class: "explorer",
			view: 'Table',
			row: {
				class: 'item'
			},
			openable:{
				enable: true
			},
			sortBy: '-modifiedDate',
			selectable: {}
		},opt);
		
		if(!(options.model instanceof Table.Model))
			options.model = new ArboModel(options.model);
			
		if(typeof options.view == 'string'){
			options.view = new Browser.Views[options.view]();
		}
		else if($.isPlainObject(options.view)){
			options.view = new Browser.Views['Table'](options.view);
		}
		
		var userFilter = options.selectable.filter;
		options.selectable.filter = function(r){
			return r.__prev === true ? false : (typeof userFilter == 'function' ? userFilter.apply(this, Array.prototype.slice.call(arguments)) : true);
		};
		
		Table.call(this,dom,options);
		
		this.$element.find('table').addClass('table');
		
	}
	inherits(Browser,Table);
	
	Browser.prototype.pwd = function(){
		return this.model().getResource(this._parent || null);
	}
	
	
	
	
	
	var ArboModel = function(options){
		
		this._options = $.extend(true,{
			filter: null, // function(resource) -> return boolean , if it returns false, the resource is ignored
			root: null, // root directory, may be a EThing.Folder instance or a string of a path or an array of resources (default to null which means the root of the user system files)
			allowTraversing: true, // display the previous directory link, no sort is made on that item : always on top (not available if root field is an array)
			flat: false,
			onUpdate: function(added, removed, updated){
				if(added.length || removed.length || updated.length) this.table().reload();
			}
		},options);
		
		
		Table.Model.call(this,this._options);
		
		this._sort = null; // by default, no sort is made
		this._filter = this._options.filter;
		
		this._onArboUpdate = this._options.onUpdate;
		
	}
	inherits(ArboModel,Table.Model);
	
	ArboModel.prototype.init = function(tableInstance){
		Table.Model.prototype.init.call(this, tableInstance);
		if(this._onArboUpdate) {
			var self = this;
			this.onArboChanged = function(event, added, removed, updated){
				if(this._filter){
					added = added.filter(this._filter);
					removed = removed.filter(this._filter);
					updated = updated.filter(this._filter);
				}
				self._onArboUpdate.call(self, added, removed, updated);
			};
			EThing.on('ething.arbo.changed',this.onArboChanged);
		}
		return EThing.arbo.load();
	}
	ArboModel.prototype.destroy = function(){
		if(this.onArboChanged) EThing.off('ething.arbo.changed',this.onArboChanged);
	}
	
	// return the keys/columns
	ArboModel.prototype.keys = function(){
		return ['name','size','modifiedDate'];
	}
	// return the number of rows, null if not known
	ArboModel.prototype.rows = function(){
		var root = this.getResource();
		return (root instanceof EThing.Folder) ? root.ls().length : ($.isArray(root) ? root.length : null);
	}
	
	ArboModel.prototype.currentFolder = function(){
		return this._currentFolder || null;
	}
	
	// return the items, may be a deferred object
	// offset and length are used for pagination
	ArboModel.prototype.data = function(parent, offset, length){
		// parent is null if root
		
		parent = this.getResource(parent);
		
		this._currentFolder = (parent instanceof EThing.Folder) ? parent : null;
		
		var children = (parent instanceof EThing.Folder) ? (this._options.flat ? parent.find() : parent.children()) : ($.isArray(parent) ? parent : []);
		
		if(this._filter)
			children = $.grep(children,this._filter)
		
		if(this._sort)
			children.sort(this._sort);
		
		if(this._options.allowTraversing && (parent instanceof EThing.Folder)){
			if(parent!==EThing.arbo.root()){
				var prev = new EThing.Folder($.extend({}, parent.parent().json(), {
						'name': '.. (go to parent directory)'
					}));
				prev.__prev = true;
				children.unshift(prev);
			}
		}
		
		// pagination
		if(typeof offset == 'number')
			children = children.slice(offset,length ? (offset+length) : undefined);
		
		return children;
	}
	// check if an item has children or not (tree model may have)
	ArboModel.prototype.hasChildren = function(item){
		return this._options.allowTraversing && !this._options.flat && (item instanceof EThing.Folder);
	}
	// sort the data
	ArboModel.prototype.sort = function(field, ascending){
		var sortfn;
		
		if(field=="size"){
			sortfn = function(a, b) {
				return (
					isFinite(a) && isFinite(b) ?
					((ascending ? 1 : -1) * (a - b)):
					NaN
				);
			};
			// special case (mix between table length & resource size)
			this._sort = function(a,b){
				a = (typeof a.size != 'undefined') ? a.size() : (typeof a.length != 'undefined' ? a.length() : null);
				b = (typeof b.size != 'undefined') ? b.size() : (typeof b.length != 'undefined' ? b.length() : null);
				return sortfn(a,b);
			};
			return;
			
		}
		else if(field=="modifiedDate" || field=="createdDate"){
			sortfn = function(a, b) {
				return (
					isFinite(a) && isFinite(b) ?
					((ascending ? 1 : -1) * ((a>b)-(a<b))):
					NaN
				);
			};
		}
		else {
			// default
			sortfn = function(a,b){
				return (ascending ? 1 : -1) * a.localeCompare(b);
			};
		}
		
		this._sort = function(a,b){
			a = (typeof a[field] != 'undefined') ? a[field]() : null;
			b = (typeof b[field] != 'undefined') ? b[field]() : null;
			return sortfn(a,b);
		};
		
	}
	// return a unique index identifying an items according to the data given in argument
	ArboModel.prototype.index = function(resource){
		var r = (resource instanceof EThing.Resource) ? resource : EThing.arbo.findOneById(resource);
		return r ? r.id() : null;
	}
	// specific
	ArboModel.prototype.getResource = function(item){
		if(!item){
			// root directory asked
			if(typeof this._options.root == 'string')
				return EThing.arbo.findOneById(this._options.root);
			if(!this._options.root)
				return EThing.arbo.root();
			return this._options.root;
		}
		if(item.__prev===true)
			return EThing.arbo.findOneById(item.id());
		return item;
	}
	ArboModel.prototype.filter = function(filter){
		if(typeof filter == 'undefined')
			return this._filter;
		else
			this._filter = filter;
	}
	
	
	
	var ArboTableView = function(opt) {
		
		opt = $.extend(true,{
			fields: {
				'icon': {
					label: "",
					get: function(r){
						return generateSvgResourceIcon(r);
					},
					class: "col-icon",
					sortable: false
				},
				'name':{
					get: function(r){
						var html = r.basename();
						
						// append the name of the creator
						var createdBy = r.createdBy();
						if(createdBy){
							var createdByRess = EThing.arbo.findOneById(createdBy);
							if(createdByRess){
								var icon;
								if(createdByRess instanceof EThing.Device)
									icon = 'phone';
								else if(createdByRess instanceof EThing.App)
									icon = 'flash';
								else
									icon = 'asterisk';
								html += '<span class="createdBy"><span class="glyphicon glyphicon-'+icon+'" aria-hidden="true"></span> '+createdByRess.name()+'</span>';
							}
						}
						
						// is public
						if(r.public()){
							html += '<span class="public"><i class="fa fa-users col-share" aria-hidden="true"></i></span>';
						}
						
						return html;
					},
					class: "col-name"
				},
				'size':{
					get: function(resource){
						if(typeof resource.size === "function"){
							return UI.sizeToString(resource.size());
						}
						else if(resource instanceof EThing.Table)
							return resource.length()+' rows';
						else if(resource instanceof EThing.Folder)
							return resource.length()+' resources';
						else
							return '-';
					},
					class: "col-size"
				},
				'modifiedDate':{
					label: "modified",
					formatter: function(v){
						return v===null ? '-' : UI.dateToString(v);
					},
					class: "col-modified"
				}
			},
			showOnlySpecifiedField: true
		},opt);
		
		Table.TableView.call(this,opt);
	}
	inherits(ArboTableView,Table.TableView);
	
	ArboTableView.prototype.createItem = function(item,index){
		var $tr = Table.TableView.prototype.createItem.call(this,item,index);
		
		$tr.attr('data-type', item.type());
		
		if(item instanceof EThing.Folder){
			// put it at the top
			var $lastFolder = this._$tbody.children('[data-type="Folder"]').not($tr).last();
			if($lastFolder.length){
				$tr.insertAfter($lastFolder);
			} else {
				this._$tbody.prepend($tr);
			}
		}
		
		return $tr;
	}
	
	
	var ArboWallView = function(opt) {
		
		this._options = $.extend(true,{
			class: 'wallview'
		},opt);
		
		Table.View.call(this);
	}
	inherits(ArboWallView,Table.View);
	
	ArboWallView.prototype.init = function($container, table){
		
		Table.View.prototype.init.call(this,$container,table);
		
		this._$grid = $('<div>').appendTo(this.$()).addClass(this._options.class).addClass('clearfix');
		
	}
	ArboWallView.prototype.clear = function(){
		this._$grid.empty();
	}
	ArboWallView.prototype.createItem = function(resource, id){
		
		var $item = $('<div>');
		
		// construct the item dom element
		
		// icon
		var $icon = $('<div>').html(generateSvgResourceIcon(resource,true)).addClass("col-icon");
		
		// name
		var $name = $('<div>').html(resource.name()).addClass("col-name");
		
		$item.append(
			$icon,
			$name
		);
		
		this._$grid.append($item);
		
		return $item;
	}
	ArboWallView.prototype.setSelectState = function(item, checked, $item){
		/*ar $icon = $item.find('.col-icon > svg').toggleClass('col-select', checked);
		$icon.replaceWith($.Browser.generateSvgResourceIcon(checked ? 'Select' : item, true));*/
	}
	
	

	
	
	Browser.Views = {
		'Wall': ArboWallView,
		'Table': ArboTableView
	};
	
	Browser.Models = {
		'Standard': ArboModel
	};
	
	
	Browser.generateSvgResourceIcon = generateSvgResourceIcon;
	
	
	/* register as a plugin in jQuery */
	
	$.Browser = Browser;
	
	$.fn.browser = function(){
		var args = [].slice.call(arguments);
		
		if (this[0]) { // this[0] is the renderTo div
			
			var instance = $(this[0]).data('browser');
			
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
			instance = new Browser(this[0],args[0],args[1],args[2],args[3],args[4],args[5],args[6]);
			$(this[0]).data('browser',instance);
			
			return this;
		}
	};
	
	
	return Browser;
	
	
	
}));
