(function (global) {
	
	
	
	var EThing = global.EThing || {};
	
	
	EThing.Rule = function(json){
		this._json = json;
		EThing.DeferredObject.call(this);
	}
	EThing.utils.inherits(EThing.Rule,EThing.DeferredObject);
	
	EThing.Rule.prototype.id = function(){
		return this._json['id'];
	}
	
	EThing.Rule.prototype.events = function(){
		return this._json['events'];
	}
	
	EThing.Rule.prototype.conditions = function(){
		return this._json['conditions'];
	}
	
	EThing.Rule.prototype.actions = function(){
		return this._json['actions'];
	}
	
	EThing.Rule.prototype.enabled = function(){
		return !!this._json['enabled'];
	}
	
	EThing.Rule.prototype.isInvalid = function(){
		// a rules is considered invalid if one of the conditions is invalid !
		var invalid = false;
		this.conditions().forEach(function(condition){
			if(condition.isInvalid === true){
				invalid = true;
				return false;
			}
		});
		return invalid;
	}
	
	/**
	 * The name of this rule.
	 * @memberof EThing.Rule
	 * @this {EThing.Rule}
	 * @returns {string}
	 */
	EThing.Rule.prototype.name = function() {
		return this._json.name;
	}
	
	/**
	 * The priority of this rule.
	 * @memberof EThing.Rule
	 * @this {EThing.Rule}
	 * @returns {number}
	 */
	EThing.Rule.prototype.priority = function() {
		return this._json.priority;
	}
	
	/**
	 * The repeat mode of this rule.
	 * @memberof EThing.Rule
	 * @this {EThing.Rule}
	 * @returns {boolean}
	 */
	EThing.Rule.prototype.repeat = function() {
		return this._json.repeat;
	}
	
	/**
	 * Create time for this rule.
	 * @memberof EThing.Rule
	 * @this {EThing.Rule}
	 * @returns {Date}
	 */
	EThing.Rule.prototype.createdDate = function() {
		return new Date(this._json.createdDate);
	}
	
	/**
	 * Return the last time this rule has been executed or null if it never happened.
	 * @memberof EThing.Rule
	 * @this {EThing.Rule}
	 * @returns {Date|null}
	 */
	EThing.Rule.prototype.executedDate = function() {
		return this._json.executedDate ? new Date(this._json.executedDate) : null;
	}
	
	/**
	 * Return the number of times this rule has been executed.
	 * @memberof EThing.Rule
	 * @this {EThing.Rule}
	 * @returns {number}
	 */
	EThing.Rule.prototype.executedCount = function() {
		return this._json.executedCount;
	}
	
	/**
	 * Remove this rule.
	 * @memberof EThing.Rule
	 * @this {EThing.Rule}
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Rule} The instance on which this method was called.
	 */
	EThing.Rule.prototype.remove = function(callback){
		return this.deferred(function(){
				return EThing.Rule.remove(this, callback);
			});
	}
	
	
	/**
	 * Update this rule attributes
	 * @memberof EThing.Rule
	 * @this {EThing.Rule}
	 * @param {} properties
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Rule} The instance on which this method was called.
	 */
	EThing.Rule.prototype.set = function(properties, callback){
		return this.deferred(function(){
				return EThing.Rule.set(this, properties, callback);
			});
	}
	
	
	var ruleConverter = function(data, xhr){
		
		if(typeof data == 'object' && data !== null){
			
			if(Array.isArray(data)){
				data = data.map(function(d){
					return new EThing.Rule(d);
				});
			}
			else {
				if( (this instanceof EThing.Rule) && this.id() === data.id ){
					// update the context and return it !
					this._json = data;
					data = this;
				} else data = new EThing.Rule(data);
			}
		}
		
		return data;
	}
	
	
	EThing.listRules = function(callback)
	{
		return EThing.request({
			'url': '/rules',
			'method': 'GET',
			'dataType': 'json',
			'converter': ruleConverter
		},callback);
	};
	
	EThing.getRule = function(a,b)
	{
		var context;
		if(a instanceof EThing.Rule){
			context = a;
			a = a.id();
		}
		else if(!EThing.utils.isId(a)) {
			throw "First argument must be a Rule object or a Rule id !";
			return;
		}
		
		var callback = b;
		
		return EThing.request({
			'url': '/rules/' + a,
			'dataType': 'json',
			'method': 'GET',
			'context': context,
			'converter': ruleConverter
		},callback);
	};
	
	
	EThing.Rule.create = function(attr, callback){
		return EThing.request({
			'url': '/rules',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': attr,
			'converter': ruleConverter
		},callback);
	}
	
	EThing.Rule.remove = function(a,b)
	{
		var context;
		if(a instanceof EThing.Rule){
			context = a;
			a = a.id();
		}
		else if(!EThing.utils.isId(a)) {
			throw "First argument must be a Rule object or a Rule id !";
			return;
		}
		
		var callback = b;
		
		return EThing.request({
			'url': '/rules/' + a,
			'method': 'DELETE',
			'context': context
		}, callback);
	};
	
	EThing.Rule.set = function(a,b,c)
	{
		var context;
		
		if(!EThing.utils.isPlainObject(b) || !b){
			throw 'Second argument must be a unempty object !';
			return;
		}
		
		if(a instanceof EThing.Rule){
			context = a;
			a = a.id();
		}
		else if(!EThing.utils.isId(a)) {
			throw "First argument must be a Rule object or a Rule id !";
			return;
		}
		
		var callback = c;
		
		return EThing.request({
			'url': '/rules/' + a,
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': b,
			'context': context,
			'headers': {
				"X-HTTP-Method-Override": "PATCH"
			},
			'converter': ruleConverter
		},callback);
	};
	
	EThing.Rule.trigger = function(signalName, callback)
	{
		return EThing.request({
			'url': '/rules/trigger/' + encodeURIComponent(signalName),
			'method': 'POST'
		},callback);
	};
	
	
	
})(this);
