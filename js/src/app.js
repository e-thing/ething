(function (global) {
	
	var EThing = global.EThing;
	
	
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
	EThing.utils.inherits(EThing.App, EThing.Resource);
	
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
	 * @param {boolean} [auth=false] wether or not attach any authentication element. Necessary if you are not using {@link EThing.request}.
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
	EThing.App.prototype.iconLink = function(auth) {
		return this._json.hasIcon ? EThing.toApiUrl('apps/'+this.id()+'/icon',auth) : null;
	}
	
	/**
	 * Returns the link to access the content.
	 * @memberof EThing.App
	 * @this {EThing.App}
	 * @param {boolean} [auth=false] wether or not attach any authentication element. Necessary if you are not using {@link EThing.request}.
	 * @returns {string}
	 * @example
	 * // using EThing.request() :
	 * EThing.request(app.getContentUrl()).done(function(content){
	 *   // success
	 *   console.log('content as text : '+content);
	 * });
	 */
	EThing.App.prototype.getContentUrl = function(auth) {
		return EThing.toApiUrl('apps/'+this.id(),auth);
	}
	
	/**
	 * Last time the content of this resource was modified
	 * @memberof EThing.App
	 * @this {EThing.App}
	 * @returns {Date}
	 */
	EThing.App.prototype.contentModifiedDate = function() {
		return new Date(this._json.contentModifiedDate);
	}
	
	/**
	 * Return the scope of this app.
	 * @memberof EThing.App
	 * @this {EThing.App}
	 * @returns {string}
	 */
	EThing.App.prototype.scope = function() {
	  return (typeof this._json.scope == 'string') ? this._json.scope : '';
	}
	
	/**
	 * Return the version of this app or null if this app is not versioned.
	 * @memberof EThing.App
	 * @this {EThing.App}
	 * @returns {string}
	 */
	EThing.App.prototype.version = function() {
	  return this._json.version || null;
	}
	
	/**
	 * Gets the code of this application in text/html.
	 * @memberof EThing.App
	 * @this {EThing.App}
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.App} The instance on which this method was called.
	 */
	EThing.App.prototype.read = function(callback){
		var args = [].slice.call(arguments);
		return this.deferred(function(){
				args.unshift(this);
				return EThing.App.read.apply(EThing, args);
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
		var args = [].slice.call(arguments);
		return this.deferred(function(){
				args.unshift(this);
				return EThing.App.write.apply(EThing, args);
			});
	}
	
	
	
	
	/**
	 * Creates a new Application from the following attributes :
	 *   - name {string} __ required__ the name of the application
	 *   - description {string} a string describing this application 
	 *   - data {object} key/value pairs to attach to this application
	 *   - content {string} the full base64 encoded script
	 *   - icon {string} the base64 encoded icon of this application
	 *
	 * @method EThing.App.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.app.created
	 * @example
	 * EThing.App.create({
     *   name: "myApp",
     *   content: "<html><body>hello world !</body></html>",
     *   icon: <icon_data>, // File, Blob, ArrayBuffer or base64 string
	 *   scope: "resource:read profile:read",
     * }).done(function(resource){
	 *     console.log('the new app can be accessed through : ' + resource.url());
	 * })
	 */
	EThing.App.create = function(json,callback){
		
		// encode the content to base64 string
		if(json.content) json.content = global.btoa(json.content);
		
		// encode the icon into base64 string
		if(json.icon){
			
			if(json.icon instanceof Blob){
				// asynchronous
				
				if(!FileReader)
					throw 'no FileReader instance found';
				var reader = new FileReader(), dfr = EThing.utils.Deferred();
				reader.onloadend = function() {
				  json.icon = reader.result.substr(reader.result.indexOf(';base64,')+8);
				  
				  EThing.request({
					'url': '/apps',
					'dataType': 'json',
					'method': 'POST',
					'contentType': "application/json; charset=utf-8",
					'data': json,
					'converter': EThing.resourceConverter
				  }).done(function(){
					dfr.resolveWith(this, Array.prototype.slice.call(arguments));
				  }).fail(function(){
					dfr.rejectWith(this, Array.prototype.slice.call(arguments));
				  });
				  
				}
				reader.readAsDataURL(json.icon);
				
				return dfr.done(callback).done(function(){
					EThing.trigger('ething.app.created',[this]);
				}).promise();
			}
			else if(json.icon instanceof ArrayBuffer){
				var binary = '',
					bytes = new Uint8Array(json.icon);
				for (var i = 0; i < bytes.byteLength; i++) {
					binary += String.fromCharCode( bytes[ i ] );
				}
				json.icon = global.btoa(binary);
			}
			else if(json.icon != 'string')
				throw 'invalid type for the icon attribute';
			
		}
		
		return EThing.request({
			'url': '/apps',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': json,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.app.created',[r]);
		});
		
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
			'url': '/apps/' + file_id,
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
			'url': '/apps/' + file_id,
			'dataType': 'json',
			'method': 'PUT',
			'contentType': (typeof b == 'string') ? 'text/plain' : 'application/octet-stream',
			'data': b,
			'context': context,
			'converter': EThing.resourceConverter
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
			'url': '/apps/' + file_id + '/icon',
			'method': 'GET',
			'dataType': EThing.utils.isNode ? 'buffer' : 'blob',
			'context': context
		},callback);
	};
	
})(this);