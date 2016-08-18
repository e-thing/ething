/**
 * EThing - javascript API of the EThing project
 * @version v0.1.0
 */
(function (global) {
	
	
	/**
	 * Contains all eThing API classes and functions.
	 * @namespace EThing
	 */
	var EThing = global.EThing || {};
	
	
	
	var extend = EThing.utils.extend;
	var isResourceId = EThing.utils.isId;
	var isPlainObject = EThing.utils.isPlainObject;
	
	
	
	/*
	* private utils
	*/
	
	function buildParams( prefix, obj, add ) {
		var name;

		if ( Array.isArray( obj ) ) {
			// Serialize array item.
			for(var i in obj){
				var v = obj[i];
				if ( /\[\]$/.test( prefix ) ) {
					// Treat each array item as a scalar.
					add( prefix, v );

				} else {
					// Item is non-scalar (array or object), encode its numeric index.
					buildParams( prefix + "[" + ( typeof v === "object" ? i : "" ) + "]", v, add );
				}
			};

		} else if ( typeof obj === "object" ) {
			// Serialize object item.
			for ( name in obj ) {
				buildParams( prefix + "[" + name + "]", obj[ name ], add );
			}

		} else {
			// Serialize scalar item.
			add( prefix, obj );
		}
	}
	var param = function(data){
		
		var prefix,
			s = [],
			add = function( key, value ) {
				// If value is a function, invoke it and return its value
				value = (typeof value == 'function') ? value() : ( value == null ? "" : value );
				s[ s.length ] = encodeURIComponent( key ) + "=" + encodeURIComponent( value );
			};

		// If traditional, encode the "old" way (the way 1.3.2 or older
		// did it), otherwise encode params recursively.
		for ( prefix in data ) {
			if(!(data[prefix] === null || typeof data[prefix] == 'undefined'))
				buildParams( prefix, data[ prefix ], add );
		}

		// Return the resulting serialization
		return s.join( "&" ).replace( /%20/g, "+" );
		
	}
	
	var ajaxSuccessHandlers = [],
		ajaxCompleteHandlers = [],
		ajaxErrorHandlers = [];
	
	
	EThing.Error = function(json){
		if(typeof json == "string")
			json = {
				message: json
			};
		extend(this, {
			message: ''
		}, json);
	}
	
	
	// only absolute url will be preserved untouched,
	// else API url is prepended
	var toUrl = function(url, auth){
		url = url || '';
		
		if(/^\/\//.test(url))
			url = EThing.Config.scheme + ':' + url;
		
		if(!/^http/.test(url)){
			// relative url
			var apiPath = EThing.Config.rootPath.replace(/\/?$/,'/api');
			if(!/^\//.test(url) && url)
				url = '/'+url;
			if(!(new RegExp('^'+apiPath)).test(url)){
				url = apiPath + url;
			}
			
			url = EThing.Config.scheme + '://' + EThing.Config.host + url;
		}
		
		if(auth && isApiUrl(url) && _token){
			url = EThing.utils.updateQueryStringParameter(url, 'access_token', _token);
		}
		
		return url;
	}
	
	// returns true if it is an URL to the HTTP API
	var isApiUrl = function(url){
		return (new RegExp('^(https?:)?//'+EThing.Config.host+EThing.Config.rootPath.replace(/\/?$/,'/api'))).test(url);
	}
	
	
	
	EThing.toApiUrl = toUrl;
	
	var ajax = function(options){
		var deferred = new EThing.utils.Deferred(),
			xhr = new XMLHttpRequest();
		
		if(typeof options == 'string')
			options = {
				url: options
			};
		
		options = extend({
			method: 'GET',
			context: null,
			url: null,
			data: null,
			contentType: null, // When sending data to the server, use this content type , default to 'application/x-www-form-urlencoded; charset=UTF-8'
			headers: null,
			dataType: null, // The type of data that you're expecting back from the server (json -> {object}, text|html -> {string} , blob|binary -> {Blob} )
			converter: null // a user defined function to convert the receive data into something else ...
		},options);
		
		
		if(typeof options.url != 'string')
			return null;
		
		var url = toUrl(options.url);
		var authentificate = isApiUrl(url);
		
		
		options.method = options.method.toUpperCase();
		
		var context = options.context || EThing;
		
		var hasContent = !/^(?:GET|HEAD)$/.test( options.method );
		
		// Convert data if not already a string, a Blob or an ArrayBuffer
		if ( options.data && typeof options.data !== "string" && !(options.data instanceof Blob) && !(options.data instanceof ArrayBuffer)){
			options.data = param( options.data );
		}
		
		
		// If data is available, append data to url
		if ( !hasContent && options.data )
			url += ( /\?/.test( url ) ? "&" : "?" ) + options.data;
		
		
		xhr.open(options.method, url, true);
		
		
		// content-type header
		if(options.contentType)
			xhr.setRequestHeader('Content-Type', options.contentType);
		else if(hasContent)
			xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
		
		// user headers
		if(isPlainObject(options.headers))
			for(var i in options.headers)
				if(options.headers.hasOwnProperty(i))
					xhr.setRequestHeader(i, options.headers[i]);
		
		// authentication
		if(authentificate){
			if(_token)
				xhr.setRequestHeader('X-ACCESS-TOKEN', _token);
		}
		
		// 
		var hasResponse = false;
		if(options.dataType == 'binary')
			options.dataType = 'blob';
		if(/blob|arraybuffer|json|text|document/i.test(options.dataType)){
			xhr.responseType = options.dataType;
			hasResponse = true;
		}
		
		function reject(){
			
			var ct = xhr.getResponseHeader("Content-Type") || '',
				data = null;
			
			if(/json/.test(ct)){
				
				switch(xhr.responseType){
					
					case '':
					case 'text':
						try{
							data = JSON.parse(xhr.responseText);
						} catch(e){}
						break;
					case 'json':
						data = xhr.response;
						break;
					case 'blob':
						data = EThing.utils.Deferred();
						
						var fileReader = new FileReader();
						fileReader.onload = function() {
							try{
								data.resolve( JSON.parse(String.fromCharCode.apply(null, new Uint8Array(this.result))) );
							} catch(e){
								data.reject();
							}
						};
						fileReader.readAsArrayBuffer(xhr.response);
						break;
					case 'arraybuffer':
						try{
							data = JSON.parse(String.fromCharCode.apply(null, new Uint8Array(this.result)));
						} catch(e){}
						break;
				}
				
			}
			
			EThing.utils.Deferred.when(data).always(function(data){
				
				var error = (isPlainObject(data) && (typeof data.message == "string")) ? data : {
						message: "unknown error"
					},
					args = [new EThing.Error(error),xhr,options];
				
				ajaxErrorHandlers.forEach(function(handler){
					handler.apply(context,args);
				});
				ajaxCompleteHandlers.forEach(function(handler){
					handler.apply(context,args);
				});
				deferred.rejectWith(context,args);
				
			});
			
			
		}
		
		function resolve(data){
			var args = [data,xhr,options];
			ajaxSuccessHandlers.forEach(function(handler){
				handler.apply(context,args);
			});
			ajaxCompleteHandlers.forEach(function(handler){
				handler.apply(context,args);
			});
			deferred.resolveWith(context,args);
		}
		
		// events
		xhr.onload=function(e){
			var success = xhr.status >= 200 && xhr.status < 300 || xhr.status === 304;
			if (success) {  
				// success
				var data = xhr.response,
					ct = xhr.getResponseHeader("Content-Type");
				
				if(!hasResponse){ // intelligent guess
					// is json data ?
					if(/json/.test(ct)){
						data = JSON.parse(data); 
					}
					else if(/xml/.test(ct)){
						data = xhr.responseXML;
					}
				}
				
				if(typeof options.converter == 'function'){
					data = options.converter.call(context,data,xhr,options);
				}
				
				resolve(data);
			}
			else
				reject();
		}
		xhr.onerror=reject;
		xhr.onabort=reject;
		xhr.onprogress=function(e){
			deferred.notifyWith(context,[e,xhr,options]);
		}
		
		
		
		xhr.send(hasContent && options.data ? options.data : null);
		
		return deferred.promise();
	}
	
	// if the argument is a json object describing a resource, then it converts it into a Resource instance, else it returns the object unchanged
	var autoConverter = function(data, xhr){
		if(!(typeof data == 'object' && data !== null))
			return data;
		
		function isResourceMetaData(json){
			if(json.hasOwnProperty('id') && json.hasOwnProperty('type') && json.hasOwnProperty('name') && json.hasOwnProperty('mime') && json.hasOwnProperty('user')){
				if(EThing.hasOwnProperty(json.type))
					return true;
				throw "Unknown type : "+json.type;
			}
			return false;
		}
		
		if(Array.isArray(data)){
			return data.map(function(d){
				return isResourceMetaData(d) ? new EThing[d.type](d) : d;
			});
		}
		else {
			if(isResourceMetaData(data)){
				if( (this instanceof EThing.Resource) && this.id() === data.id ){
					// update the context and return it !
					this._fromJson(data);
					return this;
				}
				else
					return new EThing[data.type](data);
			}
			else
				return data;
		}
	}
	
	
	
	
	/**
	 * Make a HTTP request. The options object contains the following properties :
	 *  - url {string} __required__ The url of the request. The API url will be prepended to relative URLs.
	 *  - method {string} The HTTP request method to use. Default is GET.
	 *  - data {string|object|Blob|ArrayBuffer} The query string for GET request. The HTTP request body for POST|PATCH|PUT requests. If an object is given, it will be serialized into a query string.
	 *  - contentType {string} When sending data to the server, use this content type. Default is 'application/x-www-form-urlencoded; charset=UTF-8'.
	 *  - dataType {string} The type of data that you're expecting back from the server. See {@link http://xhr.spec.whatwg.org/#the-responsetype-attribute|XMLHttpRequest standard}.
	 *  - headers {object} Additional HTTP request headers.
	 *  - context {object} The value of this provided for the call of the callbacks
	 *  - converter {function(data,XHR)} A function that returns the transformed value of the response
	 *
	 * 
	 * You may also give a callback as a second parameter. This callback is executed when the request is complete whether in failure or success.
	 * On success, it receives the returned request data, as well as the XMLHttpRequest object.
	 * On failure, the first parameter will be a Error object describing the error.
	 * To check if a request is in failure :
	 * <pre><code>EThing.request(options,function(data,xhr){
	 *     if(data instanceof EThing.Error){
	 *       // an error occurs, print the associated message
	 *       console.log(data.message);
	 *     }
	 *   })`
	 * </code></pre>
	 *
	 *
	 * This function returns a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object} object.
	 *
	 * The done|fail|always functions take the same parameters than the {@link http://api.jquery.com/category/deferred-object/|jQuery version}.
	 *
	 *
	 *
	 * @method EThing.request
	 * @param {string|object} options a set of key/value pairs that configure the request. If an URL is given, a GET request with the default options is made.
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}
	 * @example
	 * // GET request
	 * EThing.request('/resources') // is equivalent to EThing.list()
	 *
	 * // pass an object to make more complex request
	 * // store some data in a file
	 * EThing.request({
	 *   url: '/file/'+fileId,
	 *   method: 'PUT',
	 *   data: 'some content here ...',
	 *   contentType: 'text/plain'
	 * })
	 * .done(function(file){
	 *   console.log("the content was stored in the file "+file.name());
	 * })
	 * .fail(function(error){
	 *   console.log("an error occurs : "+error.message);
	 * });
	 */
	// opt : same as ajax options or an url
	EThing.request = function(opt,callback){
		var d = ajax(opt);
		
		if(typeof callback == 'function')
			d.always(function(){
				callback.apply(this,Array.prototype.slice.call(arguments));
			});
		
		return d;
	}
	
	
	/**
	 * Register a handler to be called when API requests complete.
	 *
	 * @method EThing.ajaxComplete
	 * @param {function(data,XHR,options)} handler The function to be invoked.
	 */
	EThing.ajaxComplete = function(handler){
		if(typeof handler == 'function'){
			ajaxCompleteHandlers.push(handler);
		}
	}
	/**
	 * Register a handler to be called when API requests complete successfully.
	 *
	 * @method EThing.ajaxSuccess
	 * @param {function(data,XHR,options)} handler The function to be invoked.
	 */
	EThing.ajaxSuccess = function(handler){
		if(typeof handler == 'function'){
			ajaxSuccessHandlers.push(handler);
		}
	}
	/**
	 * Register a handler to be called when API requests complete with an error.
	 *
	 * @method EThing.ajaxError
	 * @param {function(data,XHR,options)} handler The function to be invoked.
	 */
	EThing.ajaxError = function(handler){
		if(typeof handler == 'function'){
			ajaxErrorHandlers.push(handler);
		}
	}
	
	
	
	
		
	// deferred engine
	function DeferredObject(){
		
		var resolvedDfr = EThing.utils.Deferred().resolve(),
			queue = [],
			self = this;
		
		
		['done','fail','always','progress','then','state','isRejected','isResolved'].forEach(function(fctname){
			this[fctname] = function(){
				// get last deferred object in queue
				var dfr = queue.length ? queue[queue.length-1].dfr : resolvedDfr;
				
				var r = dfr[fctname].apply(self,Array.prototype.slice.call(arguments));
				
				return (typeof r == 'object') ? self : r;
			}
		}, this);
		this.promise = function(){
			return self;
		}
		
		function processQueue(){
			
			for(var i=0; i<queue.length; i++){
				
				var dfr = queue[i].dfr,
					pending = queue[i].pending,
					fn = queue[i].fn;
				
				if(pending){
					
					queue[i].pending = false;
					
					fn.call(self,self)
						.done(function(){
							
							var args = Array.prototype.slice.call(arguments);
							
							if(args.length>0 && (args[0] instanceof EThing.Resource) && args[0].id() === self.id() )
								self._fromJson(args[0].json()); // update resource metadata
							
							dfr.resolveWith(self,args);
						})
						.fail(function(){
							dfr.rejectWith(self,Array.prototype.slice.call(arguments));
						})
						.progress(function(){
							dfr.notifyWith(self,Array.prototype.slice.call(arguments));
						});
					
				}
				else {
					
					if(dfr.isResolved() || dfr.isRejected()){
						queue.splice(i, 1); // remove finished actions
						i--;
						continue;
					}
					// else busy, wait for that element to finish
					
				}
				
				break;
				
			}
		}
		
		this.deferred = function(action){
			
			// bind a new deferred object to this new action
			var dfr = new EThing.utils.Deferred();
			
			
			dfr.always(function(){
				// execute the next action
				processQueue();
			});
			
			
			// add this action to the queue 
			queue.push({
				fn: action,
				dfr: dfr,
				pending: true
			});
			
			processQueue();
			
			return this; // chainable
			
		};
		
	}

	
	
	function done(context /* , ... */){
		var args = Array.prototype.slice.call(arguments, 0);
		args.shift();
		return EThing.utils.Deferred().resolveWith(context,args).promise();
	}
	function fail(context /* , ... */){
		var args = Array.prototype.slice.call(arguments, 0);
		args.shift();
		return EThing.utils.Deferred().rejectWith(context,args).promise();
	}
	
	
	/*
	* Configuration
	*/
	
	// auto detect 
	var scripts = document.getElementsByTagName('script'), config = {
		scheme: window.location.protocol.replace(/:$/,'') || 'http',
		host: window.location.hostname,
		rootPath: '/ething'
	};
	for(var i=0, r; i<scripts.length; i++){
	  if(r = /^(.*\/)?lib\/core.js([?#].*)?$/.exec(scripts[i].src)){
		r = /^([^:]*):\/\/([^\/]+)(\/.*)?$/.exec(r[1]);
		config = {
		  scheme: r[1] || 'http',
		  host: r[2],
		  rootPath: r[3]
		}
	  }
	}
	EThing.Config = extend(config,EThing.Config);
	
	
	console.log('Config loaded :', EThing.Config);
	
	EThing.apiUrl = toUrl();
	
	
	function inherits(extended, parent){
		extended.prototype = new parent();
		extended.prototype.constructor = extended; // fix constructor property
	};
	
	
	
	
	
	
	
	
	

	/**
	 * Base class of all the resources
	 * @protected
	 * @class
	 * @memberOf EThing
	 * @param {object} json
	 */
	EThing.Resource = function (json)
	{
		this._fromJson(json);
		
		DeferredObject.call(this);
	}
	inherits(EThing.Resource,DeferredObject);
	
	// loader
	EThing.Resource.prototype._fromJson = function(json){
		this._json = extend({
			name:null,
			id:null,
			type:null,
			mime:null,
			user:null,
			createdBy:null,
			createdDate: 0,
			modifiedDate: 0,
			data: null,
			description: null,
			rules: [],
			location: null
		}, json || {});
	}
	
	
	/**
	 *  Returns the representation of this instance
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {object}
	 */
	EThing.Resource.prototype.json = function(){
		return this._json;
	}
	
	// path accessors
	/**
	 * Returns the name of this resource. A name is constructed as __PathName/FileName__.
	 * To get only the FileName, see {@link EThing.Resource#basename}.
	 * To get only the PathName, see {@link EThing.Resource#dirname}.
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.name = function() {
		return this._json.name;
	}
	/**
	 * Returns the path of this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.dirname = function() {
		return EThing.Resource.dirname(this._json.name);
	}
	/**
	 * Returns the basename of this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.basename = function() {
		return EThing.Resource.basename(this._json.name);
	}
	/**
	 * Returns the extension of this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.extension = function(){
		return EThing.Resource.extension(this._json.name);
	}
	/**
	 * Returns the id of this resource. This id is unique and immutable.
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.id = function(){
		return this._json.id;
	}
	/**
	 * Returns the id of the Device which creates it. Returns null if not.
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string|null}
	 */
	EThing.Resource.prototype.createdBy = function(){
		return this._json.createdBy ? this._json.createdBy.id : null;
	}
	
	/**
	 * Returns the user who created this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {EThing.User}
	 */
	EThing.Resource.prototype.user = function() {
		if(!this._user)
			this._user = new EThing.User(this._json.user);
		return this._user;
	}
	/**
	 *  Returns the type of this resource :
	 *  - "File"
	 *  - "Table"
	 *  - "App"
	 *  - "Device"
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.type = function() {
		return this._json.type;
	}
	/**
	 * Create time for this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {Date}
	 */
	EThing.Resource.prototype.createdDate = function() {
		return new Date(this._json.createdDate);
	}
	EThing.Resource.prototype.ctime = function(){
		return this.createdDate();
	}
	
	/**
	 * Last time this resource was modified
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {Date}
	 */
	EThing.Resource.prototype.modifiedDate = function() {
		return new Date(this._json.modifiedDate);
	}
	EThing.Resource.prototype.mtime = function(){
		return this.modifiedDate();
	}
	
	/**
	 * Returns the data attached to this resource or null if there is no data.
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {object|null}
	 */
	EThing.Resource.prototype.data = function() {
		return this._json.data || null;
	}
	/**
	 * Returns the MIME type of this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.mime = function(){
		return this._json.mime;
	}
	/**
	 * Returns the description of this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.description = function() {
		return this._json.description || "";
	}
	/**
	 * Returns the rules associated to this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {object[]}
	 */
	EThing.Resource.prototype.rules = function() {
		return Array.isArray(this._json.rules) ? this._json.rules : [];
	}
	
	/**
	 * 
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {object|string|null} Return either an object containing the coordinates or a string corresponding to the address or null if no location is defined for this resource.
	 */
	EThing.Resource.prototype.location = function() {
	  return this._json.location || null;
	}
	
	// resource modificators (async)
	/**
	 * Remove this resource.
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Resource} The instance on which this method was called.
	 * @example
	 * resource.remove().done(function(){
	 *   // the resource was successfully removed
	 * });
	 */
	EThing.Resource.prototype.remove = function(callback){
		return this.deferred(function(){
				return EThing.Resource.remove(this, callback);
			});
	}
	/**
	 * Update this resource attributes
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @param {} properties
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Resource} The instance on which this method was called.
	 * @example
	 * resource.set({
	 *   name: "newName.txt"
	 * }).done(function(){
	 *   console.log("the resource was successfully renamed to :"+this.name());
	 * });
	 */
	EThing.Resource.prototype.set = function(properties, callback){
		return this.deferred(function(){
				return EThing.Resource.set(this, properties, callback);
			});
	}
	/**
	 * Attaches persistant data to this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @param {object} data
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Resource} The instance on which this method was called.
	 * @example
	 * resource.setData({
	 *   "key": "value"
	 * }).done(function(){
	 *   // success
	 * });
	 */
	EThing.Resource.prototype.setData = function(data, callback){
		return this.set({'data':data},callback);
	}
	
	/**
	 * Constructs a File instance from an object decribing a file. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The File resource handle regular file such as image or text
	 * @memberof EThing
	 * @extends EThing.Resource
	 * @param {object} json
	 */
	EThing.File = function(json)
	{
		EThing.Resource.call(this, json);
	}
	inherits(EThing.File, EThing.Resource);
	
	/**
	 * Returns the size of this file in bytes.
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @returns {number}
	 */
	EThing.File.prototype.size = function() {
		return this._json.size;
	}
	/**
	 * Returns the amount of seconds after the last update after which this file is removed automatically, or null if this feature is not enable (no time limit).
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @returns {number|null}
	 */
	EThing.File.prototype.expireAfter = function(){
		return this._json.expireAfter || null;
	}
	
	/**
	 * If this file has a thumbnail (thumbnail is only available for file with MIME type __image/*__), it returns his link, else it returns null.
	 * 
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @param {boolean} [attachToken=false] wether or not attach the access token in the query string
	 * @returns {string|null}
	 * @example
	 * // the simple way
	 * var image = new Image();
	 * image.src = imageFile.thumbnailLink(true);
	 * document.body.appendChild(image);
	 *
	 * // the hard way
	 * EThing.request({
	 *   url: imageFile.thumbnailLink(),
	 *   dataType: "blob"
	 * }).done(function(blobData){
	 *   // success
     *   var image = new Image();
     *   image.src = window.URL.createObjectURL( blobData );
     *   
     *   document.body.appendChild(image);
	 * });
	 */
	EThing.File.prototype.thumbnailLink = function(attachToken) {
	  return this._json.hasThumbnail ? toUrl('file/'+this.id()+'/thumbnail',attachToken) : null;
	}
	
	/**
	 * Returns the link to access the content.
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @param {boolean} [attachToken=false] wether or not attach the access token in the query string
	 * @returns {string}
	 * @example
	 * // using EThing.request() :
	 * EThing.request(file.getContentUrl()).done(function(content){
	 *   // success
	 *   console.log('content as text : '+content);
	 * });
	 *
	 * // HTML <img> Tag :
	 * var image = new Image();
	 * image.src = imageFile.getContentUrl(true);
	 * document.body.appendChild(image);
	 */
	EThing.File.prototype.getContentUrl = function(attachToken) {
		return toUrl('file/'+this.id(),attachToken);
	}
	
	/**
	 * Returns true if this file has text based content.
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @returns {number}
	 */
	EThing.File.prototype.isText = function() {
		return this._json.isText;
	}
	
	// specific methods
	/**
	 * Gets the content of this file as text. If you want retrieve binary data, see {@link EThing.File#binaryRead}.
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.File} The instance on which this method was called.
	 * @example
	 * // using EThing.request() :
	 * file.read().done(function(content){
	 *   // success
	 *   console.log('content as text : '+content);
	 * });
	 *
	 */
	EThing.File.prototype.read = function(callback){
		return this.deferred(function(){
				return EThing.File.read(this, callback);
			});
	}
	
	/**
	 * Writes some content to this file.
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @param {string|blob|arraybuffer} data
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.File} The instance on which this method was called.
	 * @example
	 * // using EThing.request() :
	 * file.write("hello world !").done(function(){
	 *   // success
	 * });
	 *
	 */
	EThing.File.prototype.write = function(data, callback){
		return this.deferred(function(){
				return EThing.File.write(this, data, callback);
			});
	}
	
	/**
	 * Gets the content of this file as Blob. If you want retrieve text data, see {@link EThing.File#read}.
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.File} The instance on which this method was called.
	 * @example
	 * // using EThing.request() :
	 * file.binaryRead().done(function(contentAsBlob){
	 *   // success
	 * });
	 *
	 */
	EThing.File.prototype.binaryRead = function(callback){
		return this.deferred(function(){
				return EThing.File.binaryRead(this, callback);
			});
	}
	
	
	
	
	
	/**
	 * Constructs a Table instance from an object decribing a table. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The Table resource handle data in rows and columns
	 * @memberof EThing
	 * @extends EThing.Resource
	 * @param {object} json
	 */
	EThing.Table = function(json)
	{
		EThing.Resource.call(this, json);
	}
	inherits(EThing.Table, EThing.Resource);
	
	
	// specific methods
	/**
	 * The number of rows in this table
	 * @memberof EThing.Table
	 * @this {EThing.Table}
	 * @returns {number}
	 */
	EThing.Table.prototype.length = function(){
		return this._json['length'];
	}
	/**
	 * The maximum number of rows allowed in this table. Returns null if this feature is disable (number of rows is unlimited).
	 * @memberof EThing.Table
	 * @this {EThing.Table}
	 * @returns {number|null}
	 */
	EThing.Table.prototype.maxLength = function(){
		return this._json.maxLength;
	}
	/**
	 * Returns the amount of seconds after which a __row__ is automatically removed, or null if this feature is not enable.
	 * @memberof EThing.Table
	 * @this {EThing.Table}
	 * @returns {number}
	 */
	EThing.Table.prototype.expireAfter = function(){
		return this._json.expireAfter;
	}
	/**
	 * Returns the keys in this table. __The default keys ("id" and "date" are not listed)__.
	 * @memberof EThing.Table
	 * @this {EThing.Table}
	 * @returns {string[]}
	 */
	EThing.Table.prototype.keys = function(){
		var keys = [];
		for(var k in this._json.keys)
			if(this._json.keys.hasOwnProperty(k))
				keys.push(k);
		return keys;
	}
	/**
	 * Returns rows.
	 * @memberof EThing.Table
	 * @this {EThing.Table}
	 * @param {Object} [options] Customize the selection
	 * @param {number} [options.start=0] Position of the first rows to return. If start is negative, it starts from the end.
	 * @param {number} [options.length] Maximum number of rows to return.
	 * @param {string} [options.sort] The key on which to do the sorting, by default the sort is made by date.
	 * @param {string} [options.query] A query string to filter the results.
	 * @param {string} [options.fields] Fields of the results to return. If omitted, all the fields are returned.
	 * @param {function(data,XHR,options)} [callback] It is executed once the request is complete whether in failure or success
	 * @returns {EThing.Table} The instance on which this method was called.
	 * @example
	 * // returns all the content of a table :
	 * table.select().done(function(data){
	 *   // success
	 * });
	 *
	 * // returns the last 10 rows sorted by the "foo" column :
	 * table.select({start: -10, sort: "foo"}).done(function(data){
	 *   // success
	 * });
	 *
	 */
	EThing.Table.prototype.select = function(options,callback){
		return this.deferred(function(){
				return EThing.Table.select(this,options,callback);
			});
	}
	/**
	 * Removes one or multiple rows.
	 * @memberof EThing.Table
	 * @this {EThing.Table}
	 * @param {string|string[]} id The id of the row(s) to be removed
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Table} The instance on which this method was called.
	 * @example
	 * // removes the last 10 rows :
	 * table.select(-10).done(function(data){
	 *   this.removeRow(data.map(function(row){
	 *     return row.id;
	 *   }));
	 * });
	 *
	 */
	EThing.Table.prototype.removeRow = function(id,callback){
		return this.deferred(function(){
				return EThing.Table.removeRow(this,id,callback);
			});
	}
	/**
	 * Insert new data into the table. The data argument must be a key/value object.
	 * @memberof EThing.Table
	 * @this {EThing.Table}
	 * @param {object} data
	 * @param {string} [invalid_field] The behaviour to adopt when an invalid field name appears. The value must be one of the following : "rename","stop","skip","none".
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Table} The instance on which this method was called.
	 * @example
	 * table.insert({
	 *   'field1': "foobar",
	 *   'field2': 3.14,
	 *   'field3': true
	 * }).done(function(){
	 *   // success
	 * });
	 *
	 */
	EThing.Table.prototype.insert = function(data, callback){
		var args = Array.prototype.slice.call(arguments, 0);
		args.unshift(this);
		return this.deferred(function(){
				return EThing.Table.insert.apply(this,args);
			});
	}
	
	/**
	 * Replace the content of this table by a new set of data.
	 * @memberof EThing.Table
	 * @this {EThing.Table}
	 * @param {object[]} data
	 * @param {string} [invalid_field] The behaviour to adopt when an invalid field name appears. The value must be one of the following : "rename","stop","skip","none".
	 * @param {bool} [skip_error] Whether to skip data on error or not
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Table} The instance on which this method was called.
	 * // copy table content
	 * var tableSrc, tableDst;
	 * tableSrc.select().done(function(data){
	 *   tableDst.import(data);
	 * });
	 *
	 */
	EThing.Table.prototype.import = function(data, callback){
		var args = Array.prototype.slice.call(arguments, 0);
		args.unshift(this);
		return this.deferred(function(){
				return EThing.Table.import.apply(this,args);
			});
	}
	
	/**
	 * Returns the link to access the content.
	 * @memberof EThing.Table
	 * @this {EThing.Table}
	 * @param {boolean} [attachToken=false] wether or not attach the access token in the query string
	 * @returns {string}
	 * @example
	 * // using EThing.request() :
	 * EThing.request(table.getContentUrl()).done(function(rows){
	 *   // success, rows is an array of object 
	 *   console.log('number of rows : '+rows.length);
	 * });
	 * 
	 * // or using jQuery :
	 * $.getJSON(table.getContentUrl(true)).done(function(rows){
	 *   // success
	 * });
	 */
	EThing.Table.prototype.getContentUrl = function(attachToken) {
		return toUrl('table/'+this.id(),attachToken);
	}
	
	
	
	

	
	/**
	 * Constructs an App instance from an object decribing an application. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The App resource handle an application
	 * @memberof EThing
	 * @extends EThing.Resource
	 * @param {object} json
	 */
	EThing.App = function(json)
	{
		EThing.Resource.call(this, json);
	}
	inherits(EThing.App, EThing.Resource);
	
	// specific methods
	
	/**
	 * Returns the size of this application in bytes.
	 * @memberof EThing.App
	 * @this {EThing.App}
	 * @returns {number}
	 */
	EThing.App.prototype.size = function() {
		return this._json.size || 0;
	}
	
	/**
	 * If this application has an icon, it returns his link, else it returns null.
	 * 
	 * @memberof EThing.App
	 * @this {EThing.App}
	 * @param {boolean} [attachToken=false] wether or not attach the access token in the query string
	 * @returns {string|null}
	 * @example
	 * // the simple way
	 * var image = new Image();
	 * image.src = imageFile.iconLink(true);
	 * document.body.appendChild(image);
	 *
	 * // the hard way
	 * EThing.request({
	 *   url: imageFile.iconLink(),
	 *   dataType: "blob"
	 * }).done(function(blobData){
	 *   // success
     *   var image = new Image();
     *   image.src = window.URL.createObjectURL( blobData );
     *   
     *   document.body.appendChild(image);
	 * });
	 */
	EThing.App.prototype.iconLink = function(attachToken) {
		return this._json.hasIcon ? toUrl('app/'+this.id()+'/icon',attachToken) : null;
	}
	/**
	 * Tests if this application accept to open resources with a specific MIME type.
	 * You can use the wildcard '*' to match any characters.
	 * @memberof EThing.App
	 * @this {EThing.App}
	 * @param {string} mime The MIME type to test
	 * @returns {}
	 * @example
     * app.acceptMime('text/plain');
	 * app.acceptMime('image/*'); // accept all images
	 */
	EThing.App.prototype.acceptMime = function(mime) {
		if(Array.isArray(this._json.acceptedMime)){
			for(var i=0; i<this._json.acceptedMime.length; i++){
				var pattern = this._json.acceptedMime[i].replace('*','[-\\w]*');
				if((new RegExp('^'+pattern+'$')).test(mime))
					return true;
			}
		}
		return false;
	}
	
	/**
	 * Get back the MIME type this application accepts as an array, or null if not defined
	 * @memberof EThing.App
	 * @this {EThing.App}
	 * @returns {string[]|null}
	 */
	EThing.App.prototype.acceptedMime = function(mime) {
		return this._json.acceptedMime || [];
	}
	
	/**
	 * Gets the code of this application in text/html.
	 * @memberof EThing.App
	 * @this {EThing.App}
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.App} The instance on which this method was called.
	 */
	EThing.App.prototype.read = function(callback){
		return this.deferred(function(){
				return EThing.App.read(this,callback);
			});
	}
	
	/**
	 * Writes some HTML script in this application. Only available for {@link EThing.App#isEditable|editable app}
	 * @memberof EThing.App
	 * @this {EThing.App}
	 * @param {string} data the full HTML script
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.App} The instance on which this method was called.
	 */
	EThing.App.prototype.write = function(data, callback){
		return this.deferred(function(){
				return EThing.App.write(this,data,callback);
			});
	}
	
	/**
	 * Constructs a Device instance from an object decribing a device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The Device resource handle device
	 * @memberof EThing
	 * @extends EThing.Resource
	 * @param {object} json
	 */
	EThing.Device = function(json)
	{
		EThing.Resource.call(this, json);
	}
	inherits(EThing.Device, EThing.Resource);
	
	/**
	 * 
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @returns {string}
	 */
	EThing.Device.prototype.url = function() {
	  return this._json.url;
	}
	
	/**
	 * 
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @returns {object|null}
	 */
	EThing.Device.prototype.auth = function() {
	  return this._json.auth;
	}
	
	/**
	 * 
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @returns {string}
	 */
	EThing.Device.prototype.scope = function() {
	  return (typeof this._json.scope == 'string') ? this._json.scope : '';
	}
	
	/**
	 * 
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @returns {Date|null}
	 */
	EThing.Device.prototype.lastSeenDate = function() {
	  return (typeof this._json.lastSeenDate == 'string') ? new Date(this._json.lastSeenDate) : null;
	}
	
	/**
	 * 
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @returns {boolean}
	 */
	EThing.Device.prototype.hasBattery = function() {
	  return (typeof this._json.battery == "number") && this._json.battery >= 0 ;
	}
	
	/**
	 * 
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @returns {number}
	 */
	EThing.Device.prototype.battery = function() {
	  return this.hasBattery() ? this._json.battery : null ;
	}
	
	/**
	 * Make a HTTP request on this device. __Only available if an URL is set__, see {@link EThing.Device#create}
	 * The options are the same as the ones used in {@link EThing.request}.
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @param {string|object} options or an URL
	 * @returns {EThing.Device} The instance on which this method was called.
	 * @example
	 * // simple GET request
	 * device.request('/foo').done(function(data){
     *   // success, handle the data here
     * });
	 *
	 * // POST request
	 * device.request({
	 *   url: '/bar',
	 *   method: 'POST',
	 *   data: 'some content here ...',
	 *   contentType: 'text/plain'
	 * })
	 * .done(function(data){
	 *   // success, handle the data here
	 * })
	 * .fail(function(error){
	 *   console.log("an error occurs : "+error.message);
	 * });
	 */
	EThing.Device.prototype.request = function(settings){
		return this.deferred(function(){
				return EThing.Device.request(this,settings);
			});
	}
	EThing.Device.prototype.ajax = EThing.Device.prototype.request;
	
	EThing.Device.prototype.getResourceUrl = function(url,auth){
		return EThing.Device.getResourceUrl(this,url,auth);
	}
	
	
	
	/**
	 * Set the API descriptor of this device.
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @returns {object}
	 */
	EThing.Device.prototype.setDescriptor = function(spec,callback) {
	  if(typeof spec == 'string')
		spec = JSON.parse(spec);
	  return this.set({
		descriptor: spec
	  },callback);
	}
	
	
	
	
	
	/*
	* Resource
	*/
	
	
	
	
	
	/**
	 * This function get the available resources. A filter may be given to retrieve resources with specific attributes (see the HTTP API for more details).
	 * @method EThing.list
	 * @param {string} [query] Query string for searching resources
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @example
	 * // get all the resources
	 * EThing.list().done(function(resources){
	 *     console.log(resources);
	 * })
	 *
	 * // get only File & Table resources
	 * EThing.list('type == "File" or type == "Table"').done(function(resources){
	 *     console.log(resources);
	 * })
	 */
	EThing.list = function(a,b)
	{
		var query = null, callback = null;
		
		if(arguments.length==1){
			if(typeof arguments[0] == 'function')
				callback = arguments[0];
			else
				query = arguments[0];
		}
		else if(arguments.length>=2){
			query = arguments[0];
			callback = arguments[1];
		}
		
		return EThing.request({
			'url': '/resources?' + param({'q':query}),
			'method': 'GET',
			'converter': autoConverter
		},callback);
	};
	
	
	/**
	 * Gets an object containing informations about space usage :
	 *  - used {number} the amount of space used in bytes
	 *  - quota_size {number} the maximum space authorized in bytes
	 *
	 * @method EThing.Resource.usage
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @example
	 * // get the occupied space :
	 * EThing.Resource.usage().done(function(usage){
	 *     console.log('space used : ' + (100 * usage.used / usage.quota_size) );
	 * })
	 */
	EThing.Resource.usage = function(a)
	{
		var callback = a;
		
		return EThing.request({
			'url': '/usage',
			'method': 'GET'
		},callback);
	};
	
	
	/*
	Resource,callback
	*/
	EThing.Resource.remove = function(a,b)
	{
		var context;
		if(a instanceof EThing.Resource){
			context = a;
			a = a.id();
		}
		else if(!isResourceId(a)) {
			throw "First argument must be a Resource object or a Resource id !";
			return;
		}
		
		var callback = b;
		
		return EThing.request({
			'url': '/resources/' + a,
			'method': 'DELETE',
			'context': context
		},callback);
	};
	
	/**
	 * Gets a resource by its id.
	 *
	 * @method EThing.get
	 * @param {string|EThing.Resource} resourceIdentifier
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @example
	 * // get a resource by its id
	 * EThing.get("54516eb").done(function(resource){
	 *     console.log('the name is ' + resource.name());
	 * })
	 */
	EThing.get = function(a,b)
	{
		var context;
		if(a instanceof EThing.Resource){
			context = a;
			a = a.id();
		}
		else if(!isResourceId(a)) {
			throw "First argument must be a Resource object or a Resource id !";
			return;
		}
		
		var callback = b;
		
		return EThing.request({
			'url': '/resources/' + a,
			'method': 'GET',
			'context': context,
			'converter': autoConverter
		},callback);
	};
	
	/*
	Resource,data,callback
	*/
	EThing.Resource.set = function(a,b,c)
	{
		var context;
		
		if(!isPlainObject(b) || !b){
			throw 'Second argument must be a unempty object !';
			return;
		}
		
		if(a instanceof EThing.Resource){
			context = a;
			a = a.id();
		}
		else if(!isResourceId(a)) {
			throw "First argument must be a Resource object or a Resource id !";
			return;
		}
		
		var callback = c;
		
		return EThing.request({
			'url': '/resources/' + a,
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': JSON.stringify(b),
			'context': context,
			'headers': {
				"X-HTTP-Method-Override": "PATCH"
			},
			'converter': autoConverter
		},callback);
	};
	
	
	
	
	
	
	
	/*
	* TOOLS
	*/
	EThing.Resource.dirname = function(f) {
		var s = f.replace(/\/[^\/]*\/?$/, '');
		return ( s === f ) ? "" : s;
	}
	EThing.Resource.basename = function(f) {
		return f.replace( /.*\//, '' );
	}
	EThing.Resource.extension = function(f){
		return f.indexOf('.')>=0 ? f.split('.').pop() : '';
	}
	EThing.Resource.fnmatch = function fnmatch(pattern, path) {
		
		var patternTab = pattern.split(' ');
		var parsedPattern, regexp;
		
		for(var i=0; i<patternTab.length; i++){
			if(patternTab[i] == '') continue;
			
			parsedPattern = '^' + patternTab[i].replace(/\//g, '\\/').
			replace(/\*\*/g, '(\\/[^\\/]+)*').
			replace(/\*/g, '[^\\/]+').
			replace(/((?!\\))\?/g, '$1.') + '$';
			
			parsedPattern = '^' + parsedPattern + '$';
			
			regexp = new RegExp(parsedPattern);
			if( path.match(regexp) != null ) return true;
		}
		return false;
	};
	
	
	
	
	
	
	/*
	* File
	*/
	
	/**
	 * Creates a new File from the following attributes :
	 *   - name {string} __ required__ the name of the file
	 *   - description {string} a string describing this file 
	 *   - data {object} key/value pairs to attach to this file
	 *   - expireAfter {number} amount of seconds after the last update after which this file is removed automatically, 0 means unlimited. Default to 0.
	 *
	 * @method EThing.File.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @example
	 * EThing.File.create({
	 *   name: "foobar.txt",
	 *   description: "this is my file"
	 * }).done(function(resource){
	 *     console.log('file created : ' + resource.name());
	 * })
	 */
	EThing.File.create = function(a,callback){
		
		if(typeof a == "string")
			a = {
				'name': a
			};
		
		return EThing.request({
			'url': '/file',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': JSON.stringify(a),
			'converter': autoConverter
		},callback);
		
	};
	
	/*
	Resource,callback{function({string})}
	*/
	EThing.File.read = function(a,b)
	{
		var file_id = null, context;
		if(a instanceof EThing.File){
			context = a;
			file_id = a.id();
		}
		else if(isResourceId(a))
			file_id = a;
		else {
			throw "First argument must be a File object or a file id !";
			return;
		}
		
		var callback = b;
		
		return EThing.request({
			'url': '/file/' + file_id,
			'method': 'GET',
			'dataType': 'text',
			'context': context
		},callback);
	};
	
	/*
	Resource,callback{function({Blob})}
	*/
	EThing.File.binaryRead = function(a,b)
	{
		var file_id = null, context;
		if(a instanceof EThing.File){
			context = a;
			file_id = a.id();
		}
		else if(isResourceId(a))
			file_id = a;
		else {
			throw "First argument must be a File object or a file id !";
			return;
		}
		
		var callback = b;
		
		return EThing.request({
			'url': '/file/' + file_id,
			'method': 'GET',
			'dataType': 'blob',
			'context': context
		},callback);
		
	};

	/*
	Resource,data{string},callback{function({EThing.File})}
	*/
	EThing.File.write = function(a,b,c)
	{
		var file_id = null, context;
		if(a instanceof EThing.File){
			context = a;
			file_id = a.id();
		}
		else if(isResourceId(a))
			file_id = a;
		else {
			throw "First argument must be a File object or a file id !";
			return;
		}
		
		var callback = c;
		
		return EThing.request({
			'url': '/file/' + file_id,
			'method': 'PUT',
			'contentType': 'text/plain',
			'data': b,
			'context': context,
			'converter': autoConverter
		},callback);
	};
	
	
	
	
	/*
	* Table
	*/
	
	/**
	 * Creates a new Table from the following attributes :
	 *   - name {string} __ required__ the name of the table
	 *   - description {string} a string describing this table 
	 *   - data {object} key/value pairs to attach to this table
	 *   - expireAfter {number} amount of seconds after which a row is automatically removed, 0 means unlimited. Default to 0.
	 *   - maxLength {number} the maximum number of rows allowed in this table. 0 means unlimited. Default to 5000.
	 *
	 * @method EThing.Table.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @example
	 * // get a resource by its id
	 * EThing.Table.create({
	 *   name: "foobar",
	 *   expireAfter: 3600*24*7 // the data are automatically removed after 7 weeks
	 * }).done(function(resource){
	 *     console.log('table created : ' + resource.name());
	 * })
	 */
	EThing.Table.create = function(a,callback){
		
		if(typeof a == "string")
			a = {
				'name': a
			};
		
		return EThing.request({
			'url': '/table',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': JSON.stringify(a),
			'converter': autoConverter
		},callback);
		
	};
	
	
	EThing.Table.select = function(a,options,callback){
	
		var table_id = null, context;
		if(a instanceof EThing.Table){
			context = a;
			table_id = a.id();
		}
		else if(isResourceId(a))
			table_id = a;
		else {
			throw "First argument must be a Table object or a table id !";
			return;
		}
		
		if((typeof callback == 'undefined') && (typeof options == 'function')){
			callback = options;
			options = null;
		}
		
		options = extend({
			start: null,
			length: null,
			sort: null,
			query: null,
			fields: null
		},options);
		
		
		if(Array.isArray(options.fields)){
			options.fields = options.fields.join(',');
		}
		
		
		return EThing.request({
			'url': '/table/' + table_id + '?' + param({'start':options.start,'length':options.length,'sort':options.sort,'q':options.query,'fields':options.fields}),
			'method': 'GET',
			'context': context
		},callback);
		
	}
	
	/*
	Table,id,callback
	*/
	EThing.Table.removeRow = function(a,b,c){
	
		var table_id = null, context;
		if(a instanceof EThing.Table){
			context = a;
			table_id = a.id();
		}
		else if(isResourceId(a))
			table_id = a;
		else {
			throw "First argument must be a Table object or a table id !";
			return;
		}
		
		var id = Array.isArray(b) ? b : [b];
		var callback = c;
		
		return EThing.request({
			'url': '/table/' + table_id + '/remove',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': JSON.stringify(id),
			'context': context,
			'converter': autoConverter
		},callback);
		
	}
	
	/*
	Table,kv,callback
	Table,column,data,callback
	
	kv = {
		...
		columnX: valueX,
		...
	}
	
	Note : if valueX is null, so no data will be appended and the columnX will be created if it does not exist
	
	*/
	EThing.Table.insert = function(a,postData,c,d){
		
		var callback, table_id = null, context, invalid_field;
		
		if(a instanceof EThing.Table){
			context = a;
			table_id = a.id();
		}
		else if(isResourceId(a))
			table_id = a;
		else {
			throw "First argument must be a Table object or a table id !";
			return;
		}
		
		if( typeof c == 'string' ){
			invalid_field = c;
			callback = d;
		}
		else {
			callback = c;
		}
		
		
		return EThing.request({
			'url': '/table/' + table_id + '?' + param({'invalid_field':invalid_field}),
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': JSON.stringify(postData),
			'context': context,
			'converter': autoConverter
		},callback);
		
	}
	
	
	EThing.Table.import = function(table,data){
		var context,invalid_field,skip_error,callback;
		
		if(table instanceof EThing.Table){
			context = table;
			table = table.id();
		}
		else if(!isResourceId(table)){
			throw "First argument must be a Table object or a table id !";
			return;
		}
		
		if(!Array.isArray(data))
			throw "The data must be an array of objects";
		
		for(var i=2; i<arguments.length; i++){
			switch(typeof arguments[i]){
				case 'function':
					callback = arguments[i];
					break;
				case 'boolean':
					skip_error = arguments[i];
					break;
				case 'string':
					invalid_field = arguments[i];
					break;
			}
		}
		
		return EThing.request({
			'url': '/table/' + table + '?' + param({'skip_error':skip_error,'invalid_field':invalid_field}),
			'method': 'PUT',
			'contentType': "application/json; charset=utf-8",
			'data': JSON.stringify(data),
			'context': context,
			'converter': autoConverter
		},callback);
		
	}
	
	
	
	/*
	* Device
	*/
	
	
	/**
	 * Creates a new Device from the following attributes :
	 *   - name {string} __ required__ the name of the device
	 *   - description {string} a string describing this device 
	 *   - data {object} key/value pairs to attach to this device
	 *   - url {string} the url of this device.
	 *
	 * @method EThing.Device.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @example
	 * EThing.Device.create({
	 *   name: "foobar",
	 *   url: "123.45.67.89/device"
	 * }).done(function(resource){
	 *     console.log('the new device can be accessed through : ' + resource.url());
	 * })
	 */
	EThing.Device.create = function(a,callback){
		
		if(typeof a == "string")
			a = {
				'name': a
			};
		
		return EThing.request({
			'url': '/device',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': JSON.stringify(a),
			'converter': autoConverter
		},callback);
		
	};
	
	
	EThing.Device.getResourceUrl = function(device,url,auth){
		if(device instanceof EThing.Device){
			device = device.id();
		}
		
		var o = 'device/' + device + '/request';
		if( typeof url == 'string'){
			if(!/^\//.test(url))
				url = '/'+url;
			o += url;
		}
		return toUrl(o,auth);
	}
	
	
	/*
	device[, settings ]
	*/
	EThing.Device.ajax = EThing.Device.request = function(a,b){
		
		var devId, context;
		
		if(a instanceof EThing.Device){
			context = a;
			devId = a.id();
		}
		else if(isResourceId(a))
			devId = a;
		else {
			throw "First argument must be a Device object or a Device id !";
			return;
		}
		
		var settings = {
			'url': null,
			'context': context
		};
		
		if(typeof b == 'string')
			settings['url'] =  b;
		else
			extend(settings,b);
		
		settings['url'] = EThing.Device.getResourceUrl(devId, settings['url']);
			
		return EThing.request(settings);
		
	};
	
	
	
	/*
	* App
	*/
	
	/**
	 * Creates a new Application from the following attributes :
	 *   - name {string} __ required__ the name of the application
	 *   - description {string} a string describing this application 
	 *   - data {object} key/value pairs to attach to this application
	 *   - script {string} the full script
	 *   - acceptedMime {string[]} an array of MIME type this application can open. The wildcard '*' is allowed
	 *   - icon {string} the base64 encoded icon of this application
	 *   - version {string} the version of this application
	 *   - repository {string} the name of the repository this application is comming from
	 *   - repositoryLink {string} the URL of this application into that repository
	 *
	 * @method EThing.App.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @example
	 * EThing.App.create({
     *   name: "myApp",
     *   version: "1.0.0",
     *   script: "<html><body>hello world !</body></html>",
     *   acceptedMime: ["text/*"],
     *   icon: iconBase64
     * }).done(function(resource){
	 *     console.log('the new app can be accessed through : ' + resource.url());
	 * })
	 */
	EThing.App.create = function(json,callback){
		
		return EThing.request({
			'url': '/app',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': JSON.stringify(json),
			'converter': autoConverter
		},callback);
		
	};
	
	
	/*
	Resource,callback
	*/
	EThing.App.read = function(a,b)
	{
		var file_id = null, context;
		if(a instanceof EThing.App){
			context = a;
			file_id = a.id();
		}
		else if(isResourceId(a))
			file_id = a;
		else {
			throw "First argument must be a File object or a file id !";
			return;
		}
		
		var callback = b;
		
		return EThing.request({
			'url': '/app/' + file_id,
			'method': 'GET',
			'dataType': 'text',
			'context': context
		},callback);
	};

	/*
	Resource,data,callback
	*/
	EThing.App.write = function(a,b,c)
	{
		var file_id = null, context;
		if(a instanceof EThing.App){
			context = a;
			file_id = a.id();
		}
		else if(isResourceId(a))
			file_id = a;
		else {
			throw "First argument must be a File object or a file id !";
			return;
		}
		
		if( typeof b != 'string') {
			throw "Second argument must be a string !";
			return;
		}
		
		var callback = c;
		
		return EThing.request({
			'url': '/app/' + file_id,
			'method': 'PUT',
			'contentType': 'text/plain',
			'data': b,
			'context': context,
			'converter': autoConverter
		},callback);
	};
	
	/*
	Resource,callback
	return data as blob
	*/
	EThing.App.getIcon = function(a,b)
	{
		var file_id = null, context;
		if(a instanceof EThing.App){
			context = a;
			file_id = a.id();
		}
		else if(isResourceId(a))
			file_id = a;
		else {
			throw "First argument must be a File object or a file id !";
			return;
		}
		
		var callback = b;
		
		return EThing.request({
			'url': '/app/' + file_id + '/icon',
			'method': 'GET',
			'dataType': 'blob',
			'context': context
		},callback);
	};
	
	
	/*
	* User
	*/
	
	/**
	 * Construct a User instance. The argument must be an object representing the user with the properties id and name set.
	 * This constructor should not be used. To get the current user, use {@link EThing.auth.getUser|EThing.auth.getUser()} instead.
	 * @class Representation of an user
	 * @memberof EThing
	 * @param {object} json
	 */
	EThing.User = function(json){
		this._json = json;
	};
	
	/**
	 * Returns the representation of this instance
	 * @memberof EThing.User
	 * @this {EThing.User}
	 * @returns {object}
	 */
	EThing.User.prototype.json = function(){
		return this._json;
	}
	/**
	 * Returns the name of this user
	 * @memberof EThing.User
	 * @this {EThing.User}
	 * @returns {string} the username
	 */
	EThing.User.prototype.name = function(){
		return this._json.name;
	}
	/**
	 * Returns the id of this user
	 * @memberof EThing.User
	 * @this {EThing.User}
	 * @returns {string}
	 */
	EThing.User.prototype.id = function(){
		return this._json.id;
	}
	/**
	 * Retrieve a full representation of the current user.
	 * The returned data object is passed through the callback and contains the following properties :
	 *   - id {string}
	 *   - name {string}
	 *   - email {string}
	 *   - createdDate {Date}
	 * @memberof EThing.User
	 * @this {EThing.User}
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @example
	 * var user = EThing.auth.getUser();
	 * user.getProfile()
	 *   .done(function(profile){
	 *     var email = profile.email;
	 *     var createdDate = profile.createdDate;
	 *   })
	 */
	EThing.User.prototype.getProfile = function(callback){
		EThing.User.getProfile.call(this,callback);
	}
	
	EThing.User.prototype.set = function(data,callback){
		EThing.User.set.call(this,data,callback);
	}
	
	
	EThing.User.getProfile = function(callback){
		return EThing.request({
			'url': '/profile',
			'method': 'GET',
			'context': EThing.auth.getUser()
		},callback);
	};
	
	EThing.User.set = function(data, callback){
		
		if(!isPlainObject(data))
			throw "First argument must be an object !";
		
		
		return EThing.request({
			'url': '/profile',
			'method': 'POST',
			'context': EThing.auth.getUser(),
			'contentType': "application/json; charset=utf-8",
			'data': JSON.stringify(data),
			'headers': {
				"X-HTTP-Method-Override": "PATCH"
			},
			'converter': function(data, xhr){
				this._json = data;
				return this;
			}
		},callback);
	};
	
	
	
	/**
	 * Send a notification to the current user.
	 * @memberof EThing
	 * @param {string} [subject] The subject of the notification
	 * @param {string} message The message of the notification
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @example
	 * EThing.notify("hello world")
	 *   .done(function(){
	 *     alert("A notification has been sent");
	 *   })
	 */
	EThing.notify = function(subject,message, callback){
		var query = {};
		
		if(arguments.length == 3){
			query['body'] = message;
			query['subject'] = subject;
		}
		else if(arguments.length == 2){
			if(typeof message == 'string'){
				query['subject'] = subject;
				query['body'] = message;
			}
			else{
				query['body'] = subject;
				callback = message;
			}
		}
		else if(arguments.length == 1){
			query['body'] = subject;
		}
		else {
			throw "Bad arguments!";
			return;
		}
		
		return EThing.request({
			'url': '/notification',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': JSON.stringify(query)
		},callback);
	}
	
	
	
	
	
	/*
	 * AUTH
	 */
	
	
	// private
	var _token = null,
		_user = null;
	
	
	/**
	 * @namespace EThing.auth
	 */

	EThing.auth = {};
	
	
	
	/**
	 * Check if the user has been authenticated.
	 * @method EThing.auth.isAuthenticated
	 * @returns {boolean}
	 */
	EThing.auth.isAuthenticated = function(){
		return !!_token;
	}
	
	// return null if the JWT is invalid or expired (it is considered expired if the expiration date is before now + leeway 
	var decodeJwt = function(jwt){
		var JWS_REGEX = /^[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+$/;
		
		if(typeof jwt != 'string' || !JWS_REGEX.test(jwt))
			return null;
		
		var segments = jwt.split("."),
			jwtPayload = JSON.parse(decodeURIComponent(escape(window.atob(segments[1])))),
			now = Math.floor(Date.now() / 1000); // current timestamp
		
		return (jwtPayload && jwtPayload.hasOwnProperty('user') && typeof jwtPayload.exp == 'number' && jwtPayload.exp > now + LEENAY) ? jwtPayload : null;
	}
	
	var jwtExpireIn = function(jwt){
		var jwtPayload = decodeJwt(jwt),
			now = Math.floor(Date.now() / 1000); // current timestamp
		return (jwtPayload && typeof jwtPayload.exp == 'number') ? (jwtPayload.exp-now) : 0;
	}
	
	var refreshToken = function(){
		return ajax("auth/token")
			.done(function(data){
				// set the new token
				setToken(data.token);
			});
	};
	
	var jwtSchedulerId = null;
	
	var INTERVAL_SCHEDULER = 300;
	var LEENAY = 60;
	
	var setToken = function(jwt){
		var jwtPayload = decodeJwt(jwt);
		if(!jwtPayload)
			throw 'invalid JWT';
		
		// retrieve user public data from the jwt
		_user = new EThing.User(jwtPayload.user);
		// save the token
		_token = jwt;
		window.localStorage.setItem('auth.token',jwt);
		
		//launch the refresh token scheduler
		if(jwtSchedulerId!==null)
			window.clearTimeout(jwtSchedulerId);
		var checkJwtExpiration = function(){
			if(jwtExpireIn(_token) < 3*INTERVAL_SCHEDULER)
				refreshToken();
			jwtSchedulerId = window.setTimeout(checkJwtExpiration,INTERVAL_SCHEDULER*1000);
		}
		checkJwtExpiration();
		
		return;
	}
	
	/**
	 * Return the token (JWT) for the application.
	 * @method EThing.auth.getToken
	 * @returns {string}
	 */
	EThing.auth.getToken = function(){
		return _token;
	}
	
	/**
	 * Returns the authenticated user
	 * @method EThing.auth.getUser
	 * @returns {EThing.User} the authenticated user (or null if not authenticated)
	 * @example
	 * var user = EThing.auth.getUser();
	 * console.log(user.name());
	 */
	EThing.auth.getUser = function(){
		return _user;
	}
	
	
	/**
	 * Initiates the authorization process. If the user is not already authenticated, the browser displays a popup window prompting the user authenticate and authorize.
	 * After the user authorizes, the popup closes and the callback function fires.
	 * @param {function()} [callback] it is executed once the user is authenticated
	 * @method EThing.auth.authorize
	 * @example
	 * // start the authorization process
	 * EThing.auth.authorize(function(){
	 *   // execute your application's script here
	 * });
	 */
	EThing.auth.authorize = function(callback){
		
		var ok = function(){
			// execute the callback
			if(typeof callback == "function")
				callback.call(EThing.auth.getUser());
		}
		
		// is there a valid token in the local storage
		if(EThing.auth.isAuthenticated()){
			ok();
		}
		else {
			// need to log-in
			// open a dialog box to let the user authentificate itself
			openAuthentificateDialog(ok);
		}
		
		return;
	}
	
	/**
	 * Authenticates an user using username / password credentials.
	 * @param {string} username the user's name
	 * @param {string} password the user's password
	 * @method EThing.auth.login
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}.
	 * @example
	 * // authenticate with the user credentials
	 * EThing.auth.login("username","password")
	 * 	.done(function(user){
	 * 		// authentificated
	 * 		alert('hello '+user.name());
	 * 	})
	 * 	.fail(function(){
	 * 		// an error occurs, wrong credentials ?
	 * 	})
	 *
	 */
	EThing.auth.login = function(username,password){
		var deferred = new EThing.utils.Deferred();
		
		ajax({
			  method: "POST",
			  url: "auth/authorize",
			  contentType: "application/json; charset=utf-8",
			  data: JSON.stringify({
				'user': username,
				'password': password
			  })
			})
			.done(function(data){
				try {
					setToken(data.token);
					deferred.resolveWith(EThing,[EThing.auth.getUser()]);
				}
				catch(e){
					deferred.rejectWith(EThing,[e]);
				}
			})
			.fail(function(e){
				deferred.rejectWith(EThing,[e]);
			});
		
		return deferred.promise();
	}
	
	/**
	 * Unauthenticates a user.
	 * @method EThing.auth.logout
	 */
	EThing.auth.logout = function(){
		_token = null;
		_user = null;
		window.localStorage.removeItem('auth.token');
		if(jwtSchedulerId!==null)
			window.clearTimeout(jwtSchedulerId);
	}
	
	
	
	
	var openAuthentificateDialog = function(callback){
		
		var $title = document.createElement("h1"),
			$login = document.createElement("input"),
			$password = document.createElement("input"),
			$notification = document.createElement("div"),
			$submit = document.createElement("button"),
			$dialog = document.createElement("div"),
			$modal = document.createElement("div");
		
		$title.innerHTML = 'e-Thing';
		$submit.innerHTML = 'Login';
		
		// attributes
		$login.setAttribute('type','text');
		$login.setAttribute('placeholder','Login');
		$login.setAttribute("autofocus", "true");
		$password.setAttribute('type','password');
		$password.setAttribute('placeholder','Password');
		
		// css
		$title.style['text-align'] = 'center';
		$title.style['text-shadow'] = '1px 1px 4px rgba(150, 150, 150, 1)';
		$title.style['margin-bottom'] = '30px';
		$title.style['font-weight'] = '500';
		$notification.style.color = '#a94442';
		$notification.style.width = '100%';
		$notification.style.display = 'block';
		$notification.style['margin-bottom'] = '10px';
		$dialog.style.position = 'fixed';
		$dialog.style.top = '0px';
		$dialog.style.bottom = '0px';
		$dialog.style.left = '0px';
		$dialog.style.right = '0px';
		$dialog.style['background-color'] = '#F7F7F7';
		$dialog.style['z-index'] = '9000';
		$dialog.style['font-family'] = '"Helvetica Neue",Helvetica,Arial,sans-serif';
		$modal.style.width = '250px';
		$modal.style.margin = '40px auto';
		$submit.style.display = 'block';
		$submit.style.width = '100%';
		$submit.style.margin = '0px';
		$submit.style.padding = '10px 16px';
		$submit.style['font-size'] = '18px';
		$submit.style['line-height'] = '1.3333333';
		$submit.style['border-radius'] = '4px';
		$submit.style.color = '#fff';
		$submit.style['background-color'] = '#337ab7';
		$submit.style['border-color'] = '#2e6da4';
		$submit.style['text-align'] = 'center';
		$submit.style.cursor = 'pointer';
		$submit.style['background-image'] = 'none';
		$submit.style.border = '1px solid transparent';
		
		[$login,$password].forEach(function($e){
			$e.style.width = '100%';
			$e.style.display = 'block';
			$e.style.margin = '10px 0';
			$e.style['line-height'] = '1.42857143';
			$e.style.color = '#555',
			$e.style['background-color'] = '#fff';
			$e.style['background-image'] = 'none';
			$e.style.border = '1px solid #ccc';
			$e.style['border-radius'] = '4px';
			$e.style['box-sizing'] = 'border-box';
			$e.style.padding = '10px';
			$e.style['font-size'] = '16px';
			$e.style.height = 'auto';
		});
		
		$submit
			.addEventListener("click", function(){
				
				$notification.innerHTML = '';
				
				var login = $login.value,
					password = $password.value;
				
				if(/^\s*$/.test(login)){
					$notification.innerHTML = 'Empty login';
					return;
				}
				if(password.length==0){
					$notification.innerHTML = 'No given password';
					return;
				}
				
				EThing.auth.login(login,password)
					.done(function(){
						// remove the dialog
						if ( $dialog.parentNode )
							$dialog.parentNode.removeChild( $dialog );
						
						if(typeof callback == 'function')
							callback();
					})
					.fail(function(){
						$notification.innerHTML = 'Invalid credential';
					});
				
				
			});
		
		
		$modal.appendChild($title);
		$modal.appendChild($login);
		$modal.appendChild($password);
		$modal.appendChild($notification);
		$modal.appendChild($submit);
		
		$dialog.appendChild($modal);
		
		document.body.appendChild($dialog);
		
	}
	
	
	
	var jwt = window.localStorage.getItem('auth.token');
	var ok = function(){
		// execute the callback
		if(typeof callback == "function")
			callback.call(EThing.auth.getUser());
	}
	
	
	
	// is there a valid token in the local storage
	var _init_jwt = window.localStorage.getItem('auth.token');
	if(decodeJwt(_init_jwt)){
		// set the token
		setToken(_init_jwt);
	}
	
	
	
	
	
	
	
	
	
	
	
	
	global.EThing = EThing;
	
})(this);
