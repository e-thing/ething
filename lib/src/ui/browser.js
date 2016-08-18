(function(){
	
	var undefined;
	
	
	function inherits(extended, parent){
		extended.prototype = Object.create(parent.prototype);
	};
	
	
	
	/*
	* Browser
	*/
	
	function generateSvgResourceIcon(resource, square, style){
		var icon = {
			'File': 'F',
			'Device': 'D',
			'Table': 'T',
			'App': 'A',
			'Folder': '+',
			'Unk': '?'
		},type = typeof resource == 'string' ? resource : resource.type();
		/*return '<span class="icon-'+type+'">'+icon[type]+'</span>';
		*/
		if(!icon.hasOwnProperty(type))
			type = 'Unk';
		return '<svg class="icon-'+type+'" '+(style ? 'style="'+style+'"' : '')+' viewBox="0 0 32 32">'+(square ? '<rect x="0" y="0" width="32" height="32"/>' : '<circle cx="16" cy="16" r="16" />')+'<text x="16" y="24" font-size="22" fill="white" font-weight="bold" font-family="Arial" text-anchor="middle">'+icon[type]+'</text></svg>';
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
				enable: true,
				trigger: EThing.utils.isTouchDevice ? 'click' : 'dblclick'
			},
			sortBy: '-modifiedDate'
		},opt);
		
		if(!(options.model instanceof $.Table.Model))
			options.model = new ArboModel(options.model);
			
		if(typeof options.view == 'string'){
			options.view = new Browser.Views[options.view]();
		}
		
		$.Table.call(this,dom,options);
		
		this.$element.find('table').addClass('table table-hover');
		
	}
	inherits(Browser,$.Table);
	
	Browser.prototype.pwd = function(){
		return this.model().getResource(this._parent || null);
	}
	
	
	
	
	
	var ArboModel = function(options){
		
		this._options = $.extend(true,{
			filter: null, // function(resource) -> return boolean , if it returns false, the resource is ignored
			showParentDirectoryFolder: true, // display the previous directory link, no sort is made on that item : always on top (not available if root field is an array)
			root: null // root directory, may be a EThing.Folder instance or a string of a path or an array of resources (default to null which means the root of the user system files)
		},options);
		
		
		$.Table.Model.call(this,this._options);
		
		this._sort = null; // by default, no sort is made
		
	}
	inherits(ArboModel,$.Table.Model);
	
	ArboModel.prototype.init = function(tableInstance){
		EThing.arbo.on('resource-remove resource-add',function(){
			tableInstance.reload();
		});
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
	// return the items, may be a deferred object
	// offset and length are used for pagination
	ArboModel.prototype.data = function(parent, offset, length){
		// parent is null if root
		var deferred = $.Deferred(),
			self = this;
		
		EThing.arbo.load().done(function(){
			parent = self.getResource(parent);
			
			var children = (parent instanceof EThing.Folder) ? parent.children() : ($.isArray(parent) ? parent : []);
			
			if(self._filter || self._options.filter)
				children = $.grep(children,self._filter || self._options.filter)
			
			if(self._sort)
				children.sort(self._sort);
			
			if(self._options.showParentDirectoryFolder && (parent instanceof EThing.Folder)){
				if(parent!==EThing.arbo.root()){
					var prev = new EThing.Folder({
							'name': '.. (go to parent directory)',
							'id': '____prev____'
						});
					prev._pwd = parent.parent().id();
					children.unshift(prev);
				}
			}
			
			// pagination
			if(typeof offset == 'number')
				children = children.slice(offset,length ? (offset+length) : undefined);
			
			deferred.resolve(children);
			
		}).fail(function(){
			deferred.reject();
		});
		
		return deferred.promise();
	}
	// check if an item has children or not (tree model may have)
	ArboModel.prototype.hasChildren = function(item){
		return item instanceof EThing.Folder;
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
		else if(field=="modifiedDate"){
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
		if(item.id()==='____prev____')
			return EThing.arbo.findOneById(item._pwd);
		return item;
	}
	ArboModel.prototype.filter = function(filter){
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
					formatter: EThing.Resource.basename,
					class: "col-name"
				},
				'size':{
					get: function(resource){
						if(typeof resource.size === "function")
							return EThing.utils.sizeToString(resource.size());
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
						return v===null ? '-' : EThing.utils.dateToString(v);
					},
					class: "col-modified"
				}
			},
			showOnlySpecifiedField: true
		},opt);
		
		$.Table.TableView.call(this,opt);
	}
	inherits(ArboTableView,$.Table.TableView);
	
	
	
	
	var ArboWallView = function(opt) {
		
		this._options = $.extend(true,{
			class: 'wallview'
		},opt);
		
		$.Table.View.call(this);
	}
	inherits(ArboWallView,$.Table.View);
	
	ArboWallView.prototype.init = function($container, table){
		
		$.Table.View.prototype.init.call(this,$container,table);
		
		this._$grid = $('<div>').appendTo(this.$()).addClass(this._options.class);
		
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
	ArboWallView.prototype.setSelectState = function($item, checked){
		// todo
	}
	
	

	
	
	Browser.Views = {
		'Wall': ArboWallView,
		'Table': ArboTableView
	};
	
	
	Browser.generateSvgResourceIcon = generateSvgResourceIcon;
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery)
		window.jQuery.addPlugin('Browser',Browser);
	
	
	
})();
