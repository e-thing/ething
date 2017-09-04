
/**
 * This library helps to organise your resources in a tree structure.
 * Folders do not exist explicitly in eThing. But this library emulate it.
 * Every resource must have a name set. A name is composed of a pathname followed by a filename.
 * The pathname represent the folder where the file is located.
 *
 * For instance, the following resources :
 *    - dir1/file1.txt
 *    - dir1/file2.txt
 *    - dir2/file3.txt
 *    - file4.txt
 *
 * could be reorganized into folders:
 *
 *     root
 *      |
 *      +--dir1
 *      |    +---file1.txt
 *      |    +---file2.txt
 *      |
 *      +--dir2
 *      |    +---file3.txt
 *      |
 *      +--file4.txt
 *
 * This way, it is convenient to find all the resources located in the same folder.
 *
 * @example
 * // list all the txt files in the dir1 folder
 * EThing.arbo.load(function(){
 *   // the next line may list Table that ends with ".txt"
 *   console.log(EThing.arbo.findOne('dir1').children(/\.txt/i));
 *   // better
 *   console.log(EThing.arbo.findOne('dir1').children(function(r){
 *     return (r instanceof EThing.File) && /\.txt/i.test(r.name());
 *   }));
 * })
 *
 * @namespace {object} EThing.arbo
 */
 
(function (global) {
	
	var EThing = global.EThing || {};
	
	
	var resources = [],
		loaddfr = null,
		root = null;
	
	
	function inherits(extended, parent){
		extended.prototype = Object.create(parent.prototype);
	};
	
	/**
	 * This class is used in the {@link EThing.arbo} library. It emulates a tree structure using folders.
	 * 
	 * @protected
	 * @class
	 * @memberof EThing
	 * @extends EThing.Resource
	 * @param {Object} json
	 */
	// internal folder type
    EThing.Folder = function(json) {
		
		if(!json.id)
			json.id = '/'+json.name; // just to avoid collision beetween native resource's id and Folder's id (ie: native resource's id never has '/' character)
		
		if(json.name==='')
			this.isRoot = true;
		
		EThing.Resource.call(this,EThing.utils.extend({
			type:'Folder'
		},json));
		
	};
	inherits(EThing.Folder,EThing.Resource);
	
	/*
	* Overriding some base methods 
	*/
	
	// find the oldest createdDate
	EThing.Folder.prototype.createdDate = function() {
		var l = this.find(),
			t = null;
		for(var i=0; i<l.length; i++){
			if (t===null || t < l[i].createdDate())
				t = l[i].createdDate();
		}
		return t;
	}
	
	// Find the newest modifiedDate
	EThing.Folder.prototype.modifiedDate = function() {
		var l = this.find(),
			t = null;
		for(var i=0; i<l.length; i++){
			if (t===null || t > l[i].modifiedDate())
				t = l[i].modifiedDate();
		}
		return t;
	}
	
	
	/**
	 * Remove all the resources under this folder.
	 *
	 * @memberof EThing.Folder
	 * @this {EThing.Folder}
	 * @param {function(EThing.Folder)} [callback] function executed once the folder is removed
	 * @returns {EThing.Folder} The instance on which this method was called.
	 */
	EThing.Folder.prototype.remove = function(callback) {
		var self = this;
		return this.deferred(function(){
				var deferreds = [];
				this.children().forEach(function(r){
					deferreds.push( r.remove() );
				});
				return EThing.utils.Deferred.when.apply(EThing.utils.Deferred, deferreds).done(function(){
					if(typeof callback == 'function')
						callback.call(self);
				});
			});
	}
	
	/**
	 * This method is not applicable on folder
	 * @private
	 */
	EThing.Folder.prototype.set = null;
	/**
	 * This method is not applicable on folder
	 * @private
	 */
	EThing.Folder.prototype.setData = null;
	/**
	 * This method is not applicable on folder
	 * @private
	 */
	EThing.Folder.prototype.location;
	/**
	 * This method is not applicable on folder
	 * @private
	 */
	EThing.Folder.prototype.description;
	/**
	 * This method is not applicable on folder
	 * @private
	 */
	EThing.Folder.prototype.data;
	/**
	 * This method is not applicable on folder
	 * @private
	 */
	EThing.Folder.prototype.createdBy;
	/**
	 * This method is not applicable on folder
	 * @private
	 */
	EThing.Folder.prototype.extension = function(){
		return '';
	};
	
	
	/**
	 * List the resources and folders immediately located in this folder. This method only travels a single level down the tree.
	 * See the method {@link EThing.Folder#find} to traverse down multiple levels to select descendant elements (grandchildren, etc.).
	 *
	 * A filter can be provided, his type must be one of the following :
	 *   - function : function to test each resource. Invoked with arguments (EThing.Resource, relativeName). Return true to keep the resource, false otherwise.
	 *   - string : only the resources that match the given relative name are returned (note: two resource can have the same name).
	 *   - string[] : only the resources that match the given relative names are returned.
	 *   - RegExp : only the resources satisfying this regular expression is returned.
	 *  
	 * @memberof EThing.Folder
	 * @param {function(EThing.Resource,relativeName)|string|string[]|RegExp} [filter] if set, only the resources that match the filter are returned.
	 * @this {EThing.Folder}
	 * @returns {EThing.Resource[]}
	 */
	EThing.Folder.prototype.children = function(filter_, type){
		var fd = this._json.name.length ? (this._json.name+'/') : ''; // the root node has an empty name, no leading '/'
		var list = find(new RegExp('^'+fd+'[^/]+$'));
		if(typeof filter_ != "undefined" && filter_)
			list = list.filter(function(r){
				if(!type || r.type() === type){
					var relativeName = r.name().substr(fd.length);
					
					if(typeof filter_ == 'function'){
						return !!filter_.call(r,r,relativeName);
					}
					else if(typeof filter_ == 'string'){
						return relativeName === filter_;
					}
					else if(Array.isArray(filter_)){
						return filter_.indexOf(relativeName) >= 0;
					}
					else if(filter_ instanceof RegExp){
						return filter_.test(relativeName);
					}
				}
			});
		return list;
	}
	
	/**
	 * Synonym of {@link EThing.Folder#children}
	 * @memberof EThing.Folder
	 * @this {EThing.Folder}
	 * @returns {EThing.Resource[]}
	 */
	EThing.Folder.prototype.ls = EThing.Folder.prototype.children;
	
	/**
	 * List the resources and folders under this folder.
	 * The find() and {@link EThing.Folder#children} methods are similar, except that the latter only travels a single level down the tree.
	 *
	 * A filter can be provided, his type must be one of the following :
	 *   - function : function to test each resource. Invoked with arguments (EThing.Resource, relativeName). Return true to keep the resource, false otherwise.
	 *   - string : only the resources that match the given relative name are returned (note: two resource can have the same name).
	 *   - string[] : only the resources that match the given relative names are returned.
	 *   - RegExp : only the resources satisfying this regular expression is returned.
	 *  
	 * @memberof EThing.Folder
	 * @param {function(EThing.Resource,relativeName)|string|string[]|RegExp} [filter] if set, only the resources that match the filter are returned.
	 * @this {EThing.Folder}
	 * @returns {EThing.Resource[]}
	 */
	EThing.Folder.prototype.find = function(filter_, type){ // deep find
		var fd = this._json.name.length ? (this._json.name+'/') : ''; // the root node has an empty name, no leading '/'
		var list = find(fd.length ? new RegExp('^'+fd) : new RegExp('^.+'));
		if(typeof filter_ != "undefined" && filter_)
			list = list.filter(function(r){
				if(!type || r.type() === type){
					var relativeName = r.name().substr(fd.length);
					
					if(typeof filter_ == 'function'){
						return !!filter_.call(r,r,relativeName);
					}
					else if(typeof filter_ == 'string'){
						return relativeName === filter_;
					}
					else if(Array.isArray(filter_)){
						return filter_.indexOf(relativeName) >= 0;
					}
					else if(filter_ instanceof RegExp){
						return filter_.test(relativeName);
					}
				}
			});
		return list;
	}
	
	/**
	 * Same as {@link EThing.Folder#find} except that it will return only one result (the first resource that match the filter) or null if nothing was found.
	 * See {@link EThing.Folder#find} for more details about the argument.
	 *  
	 * @memberof EThing.Folder
	 * @param {function(EThing.Resource,relativeName)|string|string[]|RegExp} [filter] if set, only the first resource that match the filter is returned.
	 * @this {EThing.Folder}
	 * @returns {EThing.Resource|null}
	 */
	EThing.Folder.prototype.findOne = function(filter_, type){
		var res = this.find(filter_, type);
		return res.length ? res[0] : null;
	}
	
	/**
	 * Returns the number of immediate children.
	 * 
	 * @memberof EThing.Folder
	 * @this {EThing.Folder}
	 * @returns {number}
	 */
	EThing.Folder.prototype.length = function(){
		return this.children().length;
	}

	
	// extend the EThing.Resource class
	/**
	 * Returns the parent directory of this resource, Returns undefined if this resource is the root directory.
	 * 
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {EThing.Resource|undefined}
	 */
	EThing.Resource.prototype.parent = function(){
		if(!this.isRoot)
			return findOneById('/'+this.dirname());
	}
	
	
	
	
	
	function clear(){
		resources = [];
		loaddfr = null;
		root = null;
	}
	
	
	/**
	 * Load all available resources.
	 * @memberof EThing.arbo
     * @param {function(EThing.Resource[])} [callback] function executed once the resources are loaded
	 * @param {boolean} [force] force to reload the entire resources
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}.
     */
	function load(callback, force) {
		var dfr;
		
		if(loaddfr && !force){
			if(loaddfr===true)
				dfr = new EThing.utils.Deferred().resolve().promise();
			else
				dfr = loaddfr;
		}
		else {
			var pdfr = new EThing.utils.Deferred();
			
			clear();
			
			// load the resources
			EThing.request({
				'url': '/resources',
				'method': 'GET',
				'dataType': 'json'
			}).done(function(rs) {
				
				loaddfr = true;
		
				// reset everything
				resources = [];
				
				// add the root node
				root = new EThing.Folder({
					'name': ''
				});
				
				resources.push(root);
				
				// add the other resources
				rs.forEach(function(resource) {
					if(!(resource = EThing.instanciate(resource))) return;
					add(resource);
				});
				
				pdfr.resolve();
			});
			
			loaddfr = dfr = pdfr.promise();
		}
		
		return dfr.done(function() {
			if (typeof callback == 'function')
				callback(list());
			
			// trigger
			EThing.trigger('ething.arbo.loaded');
		});
	};
	
	function refresh(callback) {
		return EThing.request({
			'url': '/resources',
			'method': 'GET',
			'dataType': 'json'
		}).then(function(rs) {
			
			rs = rs.map(function(r){
				return EThing.instanciate(r);
			}).filter(function(r){
				return r;
			});
			
			update(rs, true);
			
			return resources;
		}).done(callback);
		
	}
	
	
	
	function update(newResources, replaceAll, noTrigger){
		
		if(!Array.isArray(newResources)) newResources = [newResources];
		
		var removed = [];
		var added = [];
		var updated = [];
		
		if(replaceAll){
			// check for removed resources
			// search for resources that have been deleted
			resources.forEach(function(r, index){
				
				if(r instanceof EThing.Folder) return;
				
				for(var i in newResources){
					if(newResources[i].id() === r.id()){
						return;
					}
				}
				
				removed.push(index);
			});
			
			removed.map(function(i){
				var r = resources[i];
				resources.splice(i, 1);
				return r; 
			});
		}
		
		// check for new resources or update ones
		newResources.forEach(function(r, index){
			
			var found = false;
			for(var i in resources){
				if(resources[i].id() === r.id()){
					found = i;
					break;;
				}
			}
			if(found===false){
				// new resource
				added.push(r);
				add(r);
			} else {
				// maybe updated ?
				var o = resources[found];
				if(o._fromJson(r.json())){
					updated.push(o);
				}
				newResources[index] = o;
			}
			
		});
		
		if(replaceAll){
			// remove empty folder
			for(var i=0; i<resources.length; i++){
				var r = resources[i];
				if(r instanceof EThing.Folder){
					if(r.find(function(t){return !(t instanceof EThing.Folder);}).length==0){
						removed.push(r);
						resources.splice(i, 1);
						i--;
					}
				}
			}
		}
		
		var hasChanged = removed.length>0 || added.length>0 || updated.length>0;
		
		if(!noTrigger && hasChanged){
			EThing.trigger('ething.arbo.changed', [added, removed, updated]);
		}
		
		return {
			resources : newResources,
			removed : removed,
			added : added,
			updated: updated,
			hasChanged: hasChanged
		};
	}
	
	
	function add(resource) {
		
		resources.push(resource);
		
		// check if the folder exist
		var dirname = resource.dirname();
		var f = false;
		for(var i=0; i<resources.length; i++){
			if((resources[i] instanceof EThing.Folder) && resources[i].name() === dirname){
				f = true;
				break;
			}
		}
		if(!f){
			// create the folder !
			add(new EThing.Folder({
				'name': dirname
			}));
		}
		
		return resource;
	}
	
	
	
	function remove(resource,noTraversingUp,noTrigger){
		if(Array.isArray(resource)){
			resource.forEach(function(r){
				remove(r, noTraversingUp);
			});
			return;
		}
		
		if(resource.isRoot === true) return; // do not remove the root directory !
		
		var removed = [];
		
		if(resource instanceof EThing.Folder){
			// remove all the children first !
			resource.children().forEach(function(r){
				remove(r,true);
			});
		}
		
		for (var i=0; i<resources.length; i++) {
			var r = resources[i];
			if (r.id() == resource.id()) {
				removed.push(r);
				resources.splice(i, 1);
				if(!noTraversingUp){
					// remove the associated folder ?
					var folder = r.parent();
					if(folder && folder.children().length==0){
						// this directory has no more children, remove it !
						remove(folder);
					}
				}
				break;
			}
		}
		
		if(!noTrigger && removed.length){
			EThing.trigger('ething.arbo.changed', [[], removed, []]);
		}
	}
	

	
	/**
	 * Find a resource by its unique id. For all the resources except the Folder, the id is a 7 character alphanumeric string.
	 * Since there is no duplicate name for folders, their id is equal to their name.
	 *
	 * @memberof EThing.arbo
     * @param {string} id 7 character alphanumeric string for all resources except for Folders which is their name.
	 * @return {EThing.Resource|undefined} return undefined if not found
     */
	function findOneById(w) {
		for(var i=0; i<resources.length; i++)
			if(resources[i].id() === w)
				return resources[i];
	};
	
	
	
	
	/**
	 * Returns a list of resources that pass the test implemented by the provided function or regular expression (as a string or a RegExp object).
	 * The find() method creates a new array with all the resources that pass the test implemented by the provided first argument.
	 *
	 * The test argument's type must be one of the following :
	 *   - function : function to test each resource. Invoked with arguments (EThing.Resource). Return true to keep the resource, false otherwise.
	 *   - string : only the resources that match the given relative name are returned (note: two resource can have the same name).
	 *   - string[] : only the resources that match the given relative names are returned.
	 *   - RegExp : only the resources satisfying this regular expression is returned.
	 *   - undefined : returns all the resources
	 * 
	 * @memberof EThing.arbo
     * @param {function(EThing.Resource,relativeName)|string|string[]|RegExp} [filter] only the resources that match the filter are returned.
	 * @return {EThing.Resource[]}
     */
	function find(filter, type){
		return resources.filter(function(r){
			if(!type || r.type() === type){
				var name = r.name();
				if(typeof filter == 'function'){
					return !!filter.call(r,r);
				}
				else if(typeof filter == 'string'){
					return name === filter;
				}
				else if(Array.isArray(filter)){
					return filter.indexOf(name) >= 0;
				}
				else if(filter instanceof RegExp){
					return filter.test(name);
				}
				else
					return true;
			}
			
		});
	}
	
	/**
	 * Same as {@link EThing.arbo.find} except that it will return only one result (the first resource that match the filter) or null if nothing was found.
	 * See {@link EThing.arbo.find} for more details about the argument.
	 *  
	 * @memberof EThing.arbo
	 * @param {function(EThing.Resource,relativeName)|string|string[]|RegExp} [filter] only the first resource that match the filter is returned.
	 * @returns {EThing.Resource|null}
	 */
	function findOne(filter, type){
		var res = find(filter, type);
		return res.length ? res[0] : null;
	}
	
	
	/**
	 * return all the resources. Same as {@link EThing.arbo.find|EThing.arbo.find()}.
	 * @memberof EThing.arbo
	 * @return {EThing.Resource[]}
	 */
	function list(){
		return resources;
	}
	
	
	
	
	
	
	
	
	EThing.on('ething.resource.removed', function(evt, resourceId){
		var resource = findOneById(resourceId);
		if(resource)
			remove(resource);
	});
	
	
	
	
	
	global.EThing = (global.EThing||{});
	
	global.EThing.arbo = {
		load: load,
		refresh: refresh,
		update: update,
		findOneById: findOneById,
		list: list,
		find: find,
		findOne: findOne,
		
		/**
		 * Check if the resources are loaded (ie. if the {@link EThing.arbo.load} function has been called and has returned).
		 * @memberof EThing.arbo
		 * @return {boolean}
		 */
		isLoaded: function(){
			return loaddfr === true || ( loaddfr && loaddfr.state() == 'resolved' );
		},
		
		/**
		 * Returns the root directory. If the {@link EThing.arbo.load} function was not called before, this function will return null.
		 * @memberof EThing.arbo
		 * @return {EThing.Folder|null}
		 */
		root: function(){
			return root;
		}
	};
	
	
	global.EThing = EThing;
	
})(this);
