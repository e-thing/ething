(function (global) {
	
	var EThing = global.EThing;
	
	
	
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
	EThing.utils.inherits(EThing.Table, EThing.Resource);
	
	
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
	 * Last time the content of this resource was modified
	 * @memberof EThing.Table
	 * @this {EThing.Table}
	 * @returns {Date}
	 */
	EThing.Table.prototype.contentModifiedDate = function() {
		return new Date(this._json.contentModifiedDate);
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
	 * @param {string} [options.datefmt] the format of the date field (values: "RFC3339"(default), "TIMESTAMP", "TIMESTAMP_MS", "ISO8601", "RSS").
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
		var args = [].slice.call(arguments);
		return this.deferred(function(){
				args.unshift(this);
				return EThing.Table.select.apply(EThing, args);
			});
	}
	/**
	 * Performs statistics on a specific column.
	 * @memberof EThing.Table
	 * @this {EThing.Table}
	 * @param {string} key The column name on which the statistics should be performed.
	 * @param {string} [query] A query string to filter the data.
	 * @param {function(statistics,XHR,options)} [callback] It is executed once the request is complete whether in failure or success
	 * @returns {Object} The instance on which this method was called.
	 *
	 */
	EThing.Table.prototype.computeStatistics = function(key,query,callback){
		var args = [].slice.call(arguments);
		return this.deferred(function(){
				args.unshift(this);
				return EThing.Table.computeStatistics.apply(EThing, args);
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
		var args = [].slice.call(arguments);
		return this.deferred(function(){
				args.unshift(this);
				return EThing.Table.removeRow.apply(EThing, args);
			});
	}
	/**
	 * Set new data to a row.
	 * @memberof EThing.Table
	 * @this {EThing.Table}
	 * @param {object} data the data to be updated, it must contain the row id.
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Table} The instance on which this method was called.
	 * @example
	 * table.replaceRow({
	 * 	 'id': 'g45Tdk4',
	 * 	 'value': 45
	 * }).done(function(data){
	 *   // updated !
	 * });
	 *
	 */
	EThing.Table.prototype.replaceRow = function(data,callback){
		var args = [].slice.call(arguments);
		return this.deferred(function(){
				args.unshift(this);
				return EThing.Table.replaceRow.apply(EThing, args);
			});
	}
	
	/**
	 * Finds a single row matching the query and replaces it.
	 * @memberof EThing.Table
	 * @this {EThing.Table}
	 * @param {string} query A query string to filter the data.
	 * @param {object} data the new data.
	 * @param {boolean} [upsert] If true, the data will be inserted if no match is found. (default to false).
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Table} The instance on which this method was called.
	 * @example
	 * table.findOneAndReplace("name=='foo'", {
	 * 	 'name': 'foo',
	 * 	 'value': 'bar'
	 * }).done(function(table){
	 *   // updated or inserted if not found !
	 * });
	 *
	 */
	EThing.Table.prototype.findOneAndReplace = function(query,data,upsert,callback){
		var args = [].slice.call(arguments);
		return this.deferred(function(){
				args.unshift(this);
				return EThing.Table.findOneAndReplace.apply(EThing, args);
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
		var args = [].slice.call(arguments);
		return this.deferred(function(){
			args.unshift(this);
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
		var args = [].slice.call(arguments);
		return this.deferred(function(){
			args.unshift(this);
			return EThing.Table.import.apply(this,args);
		});
	}
	
	/**
	 * Returns the link to access the content.
	 * @memberof EThing.Table
	 * @this {EThing.Table}
	 * @param {boolean} [auth=false] wether or not attach any authentication element. Necessary if you are not using {@link EThing.request}.
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
	EThing.Table.prototype.getContentUrl = function(auth) {
		return EThing.toApiUrl('tables/'+this.id(),auth);
	}
	
	
	
	
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
	 * @fires EThing#ething.table.created
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
			'url': '/tables',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.table.created',[r]);
		});
		
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
		
		options = options || {};
		
		if(Array.isArray(options.fields)){
			options.fields = options.fields.join(',');
		}
		
		
		return EThing.request({
			'url': '/tables/' + table_id + '?' + EThing.utils.param({'start':options.start,'length':options.length,'sort':options.sort,'q':options.query,'fields':options.fields,'datefmt':options.datefmt}),
			'method': 'GET',
			'dataType': 'json',
			'context': context
		},callback);
		
	}
	
	EThing.Table.computeStatistics = function(a,key,query,callback){
	
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
		
		if((typeof callback == 'undefined') && (typeof query == 'function')){
			callback = query;
			query = null;
		}
		
		
		return EThing.request({
			'url': '/tables/' + table_id + '/statistics?' + EThing.utils.param({'key':key,'q':query}),
			'method': 'GET',
			'dataType': 'json',
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
			'url': '/tables/' + table_id + '/remove',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': id,
			'context': context,
			'converter': resourceConverter
		},callback);
		
	}
	
	/*
	Table,data,callback
	*/
	EThing.Table.replaceRow = function(a,b,c){
	
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
		
		if(typeof b === 'object' && !isResourceId(b.id))
			throw "Second argument must be an object containing at least a document id";
		
		var docId = b.id
		var callback = c;
		
		return EThing.request({
			'url': '/tables/' + table_id + '/id/'+docId,
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': b,
			'context': context,
			'headers': {
				"X-HTTP-Method-Override": "PATCH"
			}
		},callback);
		
	}
	
	/*
	Table,query,data[,upsert][,callback]
	*/
	EThing.Table.findOneAndReplace = function(a,b,c,d,e){
	
		var table_id = null, context, callback = e, upsert = false;
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
		
		if(typeof b !== 'string')
			throw "Second argument must be a query string";
		
		if(typeof c !== 'object')
			throw "Third argument must be an object";
		
		if(typeof e === 'undefined' && typeof d === 'function'){
			callback = d;
			upsert = false;
		}
		if(typeof d === 'boolean') {
			upsert = d;
		}
		
		return EThing.request({
			'url': '/tables/' + table_id + '/replace?' + EThing.utils.param({'q':b, 'upsert':upsert}),
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': c,
			'context': context,
			'converter': resourceConverter
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
			'url': '/tables/' + table_id + '?' + EThing.utils.param({'invalid_field':invalid_field}),
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': postData,
			'context': context,
			'converter': resourceConverter
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
			'url': '/tables/' + table + '?' + EThing.utils.param({'skip_error':skip_error,'invalid_field':invalid_field}),
			'dataType': 'json',
			'method': 'PUT',
			'contentType': "application/json; charset=utf-8",
			'data': data,
			'context': context,
			'converter': resourceConverter
		},callback);
		
	}
	
	
	
})(this);