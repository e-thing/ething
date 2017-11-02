(function (global) {
	
	var EThing = global.EThing || {
		utils: {}
	};

	var Utils = EThing.utils;
	
	
	Utils.isNode = (typeof module !== 'undefined' && module.exports);
	
	
	Utils.isId = function(s){
		return (typeof s == 'string' && s.length === 7 && /^[0-9a-zA-Z\-_]+$/.test(s));
	}
	
	
	Utils.parseUrl = function(url){
		var r = /^((([a-z]+):)?\/\/)?(([^:]*)(:([^@]*))?@)?([^:\/?#]+)?(:([0-9]+))?([^?#]+)?(\?[^#]*)?(#.*)?$/i.exec(url);
		return r ? {
			scheme : r[3],
			user : r[5],
			password : r[7],
			hostname : r[8],
			port : r[10],
			path : r[11],
			search : r[12],
			hash: r[13]
		} : false;
	}
	
	Utils.getParam = function(url, key) {
		var queryIndex = url.indexOf('?'); 
		var regex = new RegExp("[\\?&]" + encodeURIComponent(key) + "=([^&#]*)"),
			results = queryIndex!==-1 ? regex.exec(url.substr(queryIndex)) : null;
		return results === null ? "" : decodeURIComponent(results[1]);
	}
	
	Utils.getQueryString = function(url, key) {
		var queryIndex = url.indexOf('?'); 
		var regex = new RegExp("[\\?&]" + encodeURIComponent(key) + "=([^&#]*)"),
			results = queryIndex!==-1 ? regex.exec(url.substr(queryIndex)) : null;
		return results === null ? "" : decodeURIComponent(results[1]);
	}
	
	Utils.removeParam = function(url,key){
		//prefer to use l.search if you have a location/link object
		var urlparts= url.split('?');   
		if (urlparts.length>=2) {
			
			var hashIndex = urlparts[1].indexOf('#'),
				hash = '';
			if(hashIndex !== -1){
				hash = urlparts[1].substr(hashIndex);
				urlparts[1] = urlparts[1].substr(0,hashIndex);
			}
				
			var prefix= encodeURIComponent(key)+'=';
			var pars= urlparts[1].split(/[&;]/g);

			//reverse iteration as may be destructive
			for (var i= pars.length; i-- > 0;) {    
				//idiom for string.startsWith
				if (pars[i].lastIndexOf(prefix, 0) !== -1) {  
					pars.splice(i, 1);
				}
			}

			url= urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : "") + hash;
			return url;
		} else {
			return url;
		}
	};
	
	Utils.insertParam = function(url,key,value){
		
		url = Utils.removeParam(url,key);
		
		var hashIndex = url.indexOf('#'),
			hash = '';
		if(hashIndex !== -1){ // extract hash
			hash = url.substr(hashIndex);
			url = url.substr(0,hashIndex);
		}
		
		var queryIndex = url.indexOf('?'),
			query = '';
		if(queryIndex !== -1){ // extract query
			query = url.substr(queryIndex);
			url = url.substr(0,queryIndex);
		}
		
		query += query.length ? '&' : '?';
		query += encodeURIComponent(key)+'='+encodeURIComponent(value);
		
		return url+query+hash;
	};
	
	
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
	Utils.param = function(data){
		
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
	
	
	
	
	var pad = Utils.pad = function(n, width, z) {
		z = z || '0';
		n = n + '';
		return n.length >= width ? n : new Array(width - n.length + 1)
			.join(z) + n;
	}
	
	
	Utils.sizeToString = function(s) {
		s = parseInt(s);
		if(isNaN(s)) return '-';
		var coef = 0.9;
		if (s > 1000000000 * coef)
			s = (Math.floor((s / 1000000000) * 100 ) / 100) + ' GB';
		else if (s > 1000000 * coef)
			s = (Math.floor((s / 1000000) * 100) / 100) + ' MB';
		else if (s > 1000 * coef)
			s = (Math.floor((s / 1000) * 100) / 100) + ' KB';
		else
			s = s + ' B';
		return s;
	};
	
	Utils.dateToString = function(d) {
		var now = new Date();
		
		if(typeof d == 'number'){
			d = new Date(d*1000);
		}
		
		if(!d)
			return '-';
		else if(now.getTime()-d.getTime() < 86400000){
			// 22:52
			return pad(d.getHours(),2) + ':' + pad(d.getMinutes(),2);
		}
		else {
			var curr_year = d.getFullYear();
			var curr_date = d.getDate();
			var curr_month = d.getMonth();
			
			if(curr_year == now.getFullYear()){
				// Jul. 27
				var m_names = new Array("Jan", "Feb", "Mar",
					"Apr", "May", "Jun", "Jul", "Aug", "Sep",
					"Oct", "Nov", "Dec");
				return curr_date + ' ' + m_names[curr_month] + '.';
			}
			else {
				// 2014/07/27
				return curr_year + '/' + pad(curr_month+1,2) + '/' + pad(curr_date,2);
			}
		}
	};
	
	Utils.dateDiffToString = function(diffInSec) {
		diffInSec = parseInt(diffInSec);
		if(isNaN(diffInSec)) return '-';
		// transform it into interval
		var divideBy = {
				w: 604800,
				d: 86400,
				h: 3600,
				m: 60
			},
			w = 0, // number of word
			s = '', // output string
			v;
		v = Math.floor(diffInSec / divideBy.w);
		if (v >= 1 && w < 2) {
			s += Math.floor(v) + ' week' + (v > 1 ? 's' : '');
			diffInSec -= v * divideBy.w;
			w++;
		}
		v = Math.floor(diffInSec / divideBy.d);
		if (v >= 1 && w < 2) {
			if (w) s += ' ';
			s += Math.floor(v) + ' day' + (v > 1 ? 's' : '');
			diffInSec -= v * divideBy.d;
			w++;
		}
		v = Math.floor(diffInSec / divideBy.h);
		if (v >= 1 && w < 2) {
			if (w) s += ' ';
			s += Math.floor(v) + ' hour' + (v > 1 ? 's' : '');
			diffInSec -= v * divideBy.h;
			w++;
		}
		v = Math.floor(diffInSec / divideBy.m);
		if (v >= 1 && w < 2) {
			if (w) s += ' ';
			s += Math.floor(v) + ' minute' + (v > 1 ? 's' : '');
			diffInSec -= v * divideBy.m;
			w++;
		}
		v = diffInSec;
		if (v >= 1 && w < 2) {
			if (w) s += ' ';
			s += Math.floor(v) + ' seconde' + (v > 1 ? 's' : '');
			w++;
		}

		return s;
	};
	
	
	var cache = {};// private
	
	Utils.createCache = function( requestFunction ) {
		return function( key, callback ) {
			if ( !cache[key] || (typeof cache[key].state == 'function' && cache[key].state() === 'rejected') ) {
				cache[key] = requestFunction(key);
			}
			return cache[key].done( callback );
		};
	};
	
	
	
	
	
	
	
	
	var class2type = {},
		toString = class2type.toString,
		hasOwn = class2type.hasOwnProperty;
	
	// Populate the class2type map
	"Boolean Number String Function Array Date RegExp Object Error Symbol".split(" ").forEach(function(name){
		class2type[ "[object " + name + "]" ] = name.toLowerCase();
	});
	
	
	Utils.type = function( obj ) {
		if ( obj == null ) {
			return obj + "";
		}

		// Support: Android<4.0, iOS<6 (functionish RegExp)
		return typeof obj === "object" || typeof obj === "function" ?
			class2type[ toString.call( obj ) ] || "object" :
			typeof obj;
	};
	
	Utils.isPlainObject = function( obj ) {
		var key;

		// Not plain objects:
		// - Any object or value whose internal [[Class]] property is not "[object Object]"
		// - DOM nodes
		// - window
		if ( Utils.type( obj ) !== "object" || obj.nodeType || (obj != null && obj === obj.window) ) {
			return false;
		}
		
		try {
			// Not own constructor property must be Object
			if ( obj.constructor &&
					!hasOwn.call( obj, "constructor" ) &&
					!hasOwn.call( obj.constructor.prototype || {}, "isPrototypeOf" ) ) {
				return false;
			}
		} catch ( e ) {
		  // IE8,9 Will throw exceptions on certain host objects #9897
		  return false;
		}

		// Own properties are enumerated firstly, so to speed up,
		// if last one is own, then all properties are own
		for ( key in obj ) {}

		return key === undefined || hasOwn.call( obj, key );
	};
	
	Utils.extend = function() {
		var options, name, src, copy, copyIsArray, clone,
		  target = arguments[0] || {},
		  i = 1,
		  length = arguments.length,
		  deep = false;

		// Handle a deep copy situation
		if ( typeof target === "boolean" ) {
		  deep = target;
		  target = arguments[1] || {};
		  // skip the boolean and the target
		  i = 2;
		}

		// Handle case when target is a string or something (possible in deep copy)
		if ( typeof target !== "object" && typeof target !== 'function' ) {
		  target = {};
		}

		if ( length === i ) {
		  target = this;
		  --i;
		}

		for ( ; i < length; i++ ) {
		  // Only deal with non-null/undefined values
		  if ( (options = arguments[ i ]) != null ) {
			// Extend the base object
			for ( name in options ) {
			  src = target[ name ];
			  copy = options[ name ];

			  // Prevent never-ending loop
			  if ( target === copy ) {
				continue;
			  }

			  // Recurse if we're merging plain objects or arrays
			  if ( deep && copy && ( Utils.isPlainObject(copy) || (copyIsArray = Array.isArray(copy)) ) ) {
				if ( copyIsArray ) {
				  copyIsArray = false;
				  clone = src && Array.isArray(src) ? src : [];

				} else {
				  clone = src && Utils.isPlainObject(src) ? src : {};
				}

				// Never move original objects, clone them
				target[ name ] = Utils.extend( deep, clone, copy );

			  // Don't bring in undefined values
			  } else if ( copy !== undefined ) {
				target[ name ] = copy;
			  }
			}
		  }
		}
		// Return the modified object
		return target;
	};
	
	Utils.isEqual = function(x, y) {
		'use strict';

		if (x === null || x === undefined || y === null || y === undefined) { return x === y; }
		// after this just checking type of one would be enough
		if (x.constructor !== y.constructor) { return false; }
		// if they are functions, they should exactly refer to same one (because of closures)
		if (x instanceof Function) { return x === y; }
		// if they are regexps, they should exactly refer to same one (it is hard to better equality check on current ES)
		if (x instanceof RegExp) { return x === y; }
		if (x === y || x.valueOf() === y.valueOf()) { return true; }
		if (Array.isArray(x) && x.length !== y.length) { return false; }

		// if they are dates, they must had equal valueOf
		if (x instanceof Date) { return false; }

		// if they are strictly equal, they both need to be object at least
		if (!(x instanceof Object)) { return false; }
		if (!(y instanceof Object)) { return false; }

		// recursive object equality check
		var p = Object.keys(x);
		return Object.keys(y).every(function (i) { return p.indexOf(i) !== -1; }) &&
			p.every(function (i) { return Utils.isEqual(x[i], y[i]); });
	}
	
	
	Utils.inherits = function (extended, parent){
		extended.prototype = new parent();
		extended.prototype.constructor = extended; // fix constructor property
	};
	
	global.EThing = EThing;
	
	
})(this);

(function (global) {



if(typeof module !== 'undefined' && module.exports){
	
	global.btoa = function (str) {
		var buffer;
		if (str instanceof Buffer) {
			buffer = str;
		} else {
			buffer = new Buffer(str.toString(), 'binary');
		}
		return buffer.toString('base64');
	};
	
	global.atob = function (str) {
		return new Buffer(str, 'base64').toString('binary');
	};
	
	

	var Url = require("url");

	var XMLHttpRequest = function() {
	  "use strict";

	  /**
	   * Private variables
	   */
	  var self = this;
	  var http = require("http");
	  var https = require("https");

	  // Holds http.js objects
	  var request;
	  var response;

	  // Request settings
	  var settings = {};

	  // Set some default headers
	  var defaultHeaders = {
		"User-Agent": "node-XMLHttpRequest",
		"Accept": "*/*",
	  };

	  var headers = {};
	  var headersCase = {};

	  // Send flag
	  var sendFlag = false;
	  // Error flag, used when errors occur or abort is called
	  var errorFlag = false;

	  // Event listeners
	  var listeners = {};

	  /**
	   * Constants
	   */

	  this.UNSENT = 0;
	  this.OPENED = 1;
	  this.HEADERS_RECEIVED = 2;
	  this.LOADING = 3;
	  this.DONE = 4;

	  /**
	   * Public vars
	   */

	  // Current state
	  this.readyState = this.UNSENT;

	  // default ready state change handler in case one is not set or is set late
	  this.onreadystatechange = null;

	  // Result & response
	  this.responseType = '';
	  this.response = "";
	  this.responseText = "";
	  this.status = null;
	  this.statusText = null;
	  
	  // Whether cross-site Access-Control requests should be made using
	  // credentials such as cookies or authorization headers
	  this.withCredentials = false;
	  

	  /**
	   * Public methods
	   */

	  /**
	   * Open the connection. Currently supports local server requests.
	   *
	   * @param string method Connection method (eg GET, POST)
	   * @param string url URL for the connection.
	   * @param boolean async Asynchronous connection. Default is true.
	   * @param string user Username for basic authentication (optional)
	   * @param string password Password for basic authentication (optional)
	   */
	  this.open = function(method, url, async, user, password) {
		this.abort();
		errorFlag = false;

		settings = {
		  "method": method,
		  "url": url.toString(),
		  "async": (typeof async !== "boolean" ? true : async),
		  "user": user || null,
		  "password": password || null
		};

		setState(this.OPENED);
	  };


	  /**
	   * Sets a header for the request or appends the value if one is already set.
	   *
	   * @param string header Header name
	   * @param string value Header value
	   */
	  this.setRequestHeader = function(header, value) {
		if (this.readyState !== this.OPENED) {
		  throw new Error("INVALID_STATE_ERR: setRequestHeader can only be called when state is OPEN");
		}
		if (sendFlag) {
		  throw new Error("INVALID_STATE_ERR: send flag is true");
		}
		header = headersCase[header.toLowerCase()] || header;
		headersCase[header.toLowerCase()] = header;
		headers[header] = headers[header] ? headers[header] + ', ' + value : value;
	  };

	  /**
	   * Gets a header from the server response.
	   *
	   * @param string header Name of header to get.
	   * @return string Text of the header or null if it doesn't exist.
	   */
	  this.getResponseHeader = function(header) {
		if (typeof header === "string"
		  && this.readyState > this.OPENED
		  && response
		  && response.headers
		  && response.headers[header.toLowerCase()]
		  && !errorFlag
		) {
		  return response.headers[header.toLowerCase()];
		}

		return null;
	  };

	  /**
	   * Gets all the response headers.
	   *
	   * @return string A string with all response headers separated by CR+LF
	   */
	  this.getAllResponseHeaders = function() {
		if (this.readyState < this.HEADERS_RECEIVED || errorFlag) {
		  return "";
		}
		var result = "";

		for (var i in response.headers) {
		  // Cookie headers are excluded
		  if (i !== "set-cookie" && i !== "set-cookie2") {
			result += i + ": " + response.headers[i] + "\r\n";
		  }
		}
		return result.substr(0, result.length - 2);
	  };

	  /**
	   * Gets a request header
	   *
	   * @param string name Name of header to get
	   * @return string Returns the request header or empty string if not set
	   */
	  this.getRequestHeader = function(name) {
		if (typeof name === "string" && headersCase[name.toLowerCase()]) {
		  return headers[headersCase[name.toLowerCase()]];
		}

		return "";
	  };

	  /**
	   * Sends the request to the server.
	   *
	   * @param string data Optional data to send as request body.
	   */
	  this.send = function(data) {
		if (this.readyState !== this.OPENED) {
		  throw new Error("INVALID_STATE_ERR: connection must be opened before send() is called");
		}

		if (sendFlag) {
		  throw new Error("INVALID_STATE_ERR: send has already been called");
		}

		var ssl = false;
		var url = Url.parse(settings.url);
		var host;
		// Determine the server
		switch (url.protocol) {
		  case "https:":
			ssl = true;
			// SSL & non-SSL both need host, no break here.
		  case "http:":
			host = url.hostname;
			break;

		  case undefined:
		  case null:
		  case "":
			host = "localhost";
			break;

		  default:
			throw new Error("Protocol not supported.");
		}

		// Default to port 80. If accessing localhost on another port be sure
		// to use http://localhost:port/path
		var port = url.port || (ssl ? 443 : 80);
		// Add query string if one is used
		var uri = url.pathname + (url.search ? url.search : "");

		// Set the defaults if they haven't been set
		for (var name in defaultHeaders) {
		  if (!headersCase[name.toLowerCase()]) {
			headers[name] = defaultHeaders[name];
		  }
		}

		// Set the Host header or the server may reject the request
		headers.Host = host;
		if (!((ssl && port === 443) || port === 80)) {
		  headers.Host += ":" + url.port;
		}

		// Set Basic Auth if necessary
		if (settings.user) {
		  if (typeof settings.password === "undefined") {
			settings.password = "";
		  }
		  var authBuf = new Buffer(settings.user + ":" + settings.password);
		  headers.Authorization = "Basic " + authBuf.toString("base64");
		}

		// Set content length header
		if (settings.method === "GET" || settings.method === "HEAD") {
		  data = null;
		} else if (data) {
		  headers["Content-Length"] = Buffer.isBuffer(data) ? data.length : Buffer.byteLength(data);

		  if (!headers["Content-Type"]) {
			headers["Content-Type"] = "text/plain;charset=UTF-8";
		  }
		} else if (settings.method === "POST") {
		  // For a post with no data set Content-Length: 0.
		  // This is required by buggy servers that don't meet the specs.
		  headers["Content-Length"] = 0;
		}

		var options = {
		  host: host,
		  port: port,
		  path: uri,
		  method: settings.method,
		  headers: headers,
		  agent: false,
		  withCredentials: self.withCredentials
		};

		// Reset error flag
		errorFlag = false;

		// Handle async requests
		if (settings.async) {
		  // Use the proper protocol
		  var doRequest = ssl ? https.request : http.request;

		  // Request is being sent, set send flag
		  sendFlag = true;

		  // As per spec, this is called here for historical reasons.
		  self.dispatchEvent("readystatechange");

		  // Handler for the response
		  var responseHandler = function responseHandler(resp) {
			  
			var responseData = [];
			
			// Set response var to the response we got back
			// This is so it remains accessable outside this scope
			response = resp;
			// Check for redirect
			// @TODO Prevent looped redirects
			if (response.statusCode === 301 || response.statusCode === 302 || response.statusCode === 303 || response.statusCode === 307) {
			  // Change URL to the redirect location
			  settings.url = response.headers.location;
			  var url = Url.parse(settings.url);
			  // Set host var in case it's used later
			  host = url.hostname;
			  // Options for the new request
			  var newOptions = {
				hostname: url.hostname,
				port: url.port,
				path: url.path,
				method: response.statusCode === 303 ? "GET" : settings.method,
				headers: headers,
				withCredentials: self.withCredentials
			  };

			  // Issue the new request
			  request = doRequest(newOptions, responseHandler).on("error", errorHandler);
			  request.end();
			  // @TODO Check if an XHR event needs to be fired here
			  return;
			}

			//response.setEncoding("utf8");
			
			setState(self.HEADERS_RECEIVED);
			
			self.status = response.statusCode;
			self.statusText = response.statusMessage;

			response.on("data", function(chunk) {
			  // Make sure there's some data
			  if (chunk) {
				responseData.push(chunk);
				//self.responseText += chunk;
			  }
			  // Don't emit state changes if the connection has been aborted.
			  if (sendFlag) {
				setState(self.LOADING);
			  }
			});

			response.on("end", function() {
			  //at this point data is an array of Buffers
			  //so Buffer.concat() can make us a new Buffer
			  //of all of them together
			  responseData = Buffer.concat(responseData);
			  
			  switch(self.responseType){
				case '':
				case 'text':
					self.response = responseData.toString("utf8");
					self.responseText = self.response;
					break;
				case 'json':
					try {
						self.response = JSON.parse( responseData.toString("utf8") );
					} catch(error){
						self.handleError(error);
					}
					break;
				case 'arraybuffer':
					var ab = new ArrayBuffer(responseData.length);
					var view = new Uint8Array(ab);
					for (var i = 0; i < responseData.length; ++i) {
						view[i] = responseData[i];
					}
					self.response = ab;
					break;
				case 'buffer':
					self.response = responseData;
					break;
				default:
					throw new Error(self.responseType+" response type not supported.");
					break;
			  }
			  
			  if (sendFlag) {
				// Discard the end event if the connection has been aborted
				setState(self.DONE);
				sendFlag = false;
			  }
			});

			response.on("error", function(error) {
			  self.handleError(error);
			});
		  };

		  // Error handler for the request
		  var errorHandler = function errorHandler(error) {
			self.handleError(error);
		  };

		  // Create the request
		  request = doRequest(options, responseHandler).on("error", errorHandler);

		  // Node 0.4 and later won't accept empty data. Make sure it's needed.
		  if (data) {
			request.write(data);
		  }

		  request.end();

		  self.dispatchEvent("loadstart");
		} else { // Synchronous
			
			throw new Error("Synchronous mode not supported.");
		}
		
	  };

	  /**
	   * Called when an error is encountered to deal with it.
	   */
	  this.handleError = function(error) {
		this.status = 0;
		this.statusText = error;
		this.responseText = error.stack;
		errorFlag = true;
		setState(this.DONE);
		this.dispatchEvent('error');
	  };

	  /**
	   * Aborts a request.
	   */
	  this.abort = function() {
		if (request) {
		  request.abort();
		  request = null;
		}

		headers = defaultHeaders;
		this.status = 0;
		this.responseText = "";

		errorFlag = true;

		if (this.readyState !== this.UNSENT
			&& (this.readyState !== this.OPENED || sendFlag)
			&& this.readyState !== this.DONE) {
		  sendFlag = false;
		  setState(this.DONE);
		}
		this.readyState = this.UNSENT;
		this.dispatchEvent('abort');
	  };

	  /**
	   * Adds an event listener. Preferred method of binding to events.
	   */
	  this.addEventListener = function(event, callback) {
		if (!(event in listeners)) {
		  listeners[event] = [];
		}
		// Currently allows duplicate callbacks. Should it?
		listeners[event].push(callback);
	  };

	  /**
	   * Remove an event callback that has already been bound.
	   * Only works on the matching funciton, cannot be a copy.
	   */
	  this.removeEventListener = function(event, callback) {
		if (event in listeners) {
		  // Filter will return a new array with the callback removed
		  listeners[event] = listeners[event].filter(function(ev) {
			return ev !== callback;
		  });
		}
	  };

	  /**
	   * Dispatch any events, including both "on" methods and events attached using addEventListener.
	   */
	  this.dispatchEvent = function(event) {
		if (typeof self["on" + event] === "function") {
		  self["on" + event]();
		}
		if (event in listeners) {
		  for (var i = 0, len = listeners[event].length; i < len; i++) {
			listeners[event][i].call(self);
		  }
		}
	  };

	  /**
	   * Changes readyState and calls onreadystatechange.
	   *
	   * @param int state New state
	   */
	  var setState = function(state) {
		if (state == self.LOADING || self.readyState !== state) {
		  self.readyState = state;

		  if (settings.async || self.readyState < self.OPENED || self.readyState === self.DONE) {
			self.dispatchEvent("readystatechange");
		  }

		  if (self.readyState === self.DONE && !errorFlag) {
			self.dispatchEvent("load");
			// @TODO figure out InspectorInstrumentation::didLoadXHR(cookie)
			self.dispatchEvent("loadend");
		  }
		}
	  };
	};
	
	
	
	global.XMLHttpRequest = XMLHttpRequest;
	
}
	
	
})(this);

(function (global) {
	
	
	var EThing = global.EThing || {};
	
	
	
	function returnTrue() {
		return true;
	}

	function returnFalse() {
		return false;
	}
	
	
	/*
	Event object
	*/
	
	EThing.Event = function( src, props ) {

		// Allow instantiation without the 'new' keyword
		if ( !( this instanceof EThing.Event ) ) {
			return new EThing.Event( src, props );
		}

		// Event type
		this.type = src;

		// Put explicitly provided properties onto the event object
		if ( props ) {
			EThing.utils.extend( this, props );
		}

		// Create a timestamp if incoming event doesn't have one
		this.timeStamp = Date.now();
		
	};

	EThing.Event.prototype = {
		constructor: EThing.Event,
		isDefaultPrevented: returnFalse,
		isPropagationStopped: returnFalse,
		isImmediatePropagationStopped: returnFalse,

		preventDefault: function() {
			this.isDefaultPrevented = returnTrue;
		},
		stopPropagation: function() {
			this.isPropagationStopped = returnTrue;
		},
		stopImmediatePropagation: function() {
			this.isImmediatePropagationStopped = returnTrue;
			this.stopPropagation();
		}
	};
	
	
	
	function EventEngine(obj){
		
		var event_map = {};
		
		obj.on = function(events, handler) {
			if(typeof handler == 'function'){
				events = events.split(' ');
				for(var i=0; i<events.length; i++){
					var event = events[i];
					if(event.length){
						if(!event_map[event]) event_map[event] = [];
						event_map[event].push(handler);
					}
				}
			}
		}
		
		obj.off = function(events, handler) {
			events = events.split(' ');
			for(var i=0; i<events.length; i++){
				var event = events[i];
				if(event.length && event_map[event]){
					if(typeof handler == 'function'){
						for(var j=0; j<event_map[event].length; j++){
							if(event_map[event][j]===handler){
								event_map[event].splice(j, 1);
								j--;
							}
						}
					}
					else {
						event_map[event] = [];
					}
				}
			}
		}
		
		obj.one = function(events, handler) {
			if(typeof handler == 'function'){
				obj.on(events, function(){
					obj.off(events,handler);
					handler.apply(this,Array.prototype.slice.call(arguments));
				});
			}
		}
		
		obj.trigger = function(event, extraParameters){
			if(typeof event === 'string')
				event = EThing.Event(event);
			
			var type = event.type,
				h = event_map[type] || [];
			
			for(var i=0; i<h.length; i++){
				var args = [event];
				if(Array.isArray(extraParameters))
					args = args.concat(extraParameters);
				h[i].apply(obj,args);
				
				if(event.isImmediatePropagationStopped() || event.isPropagationStopped())
					break;
			}
			return event;
		}
		
		
	}
	
	/**
	 * register an handler to an event.
	 * @name on
	 * @memberof EThing
	 * @param {string} event event type string. Multiple space separated events can be given.
	 * @param {function(EThing.Event)} handler the function to be called when the event has been triggered.
	 */
	
	/**
	 * Remove an event handler.
	 * @name off
	 * @memberof EThing
	 * @param {string} event event type string. Multiple space separated events can be given.
	 * @param {function(EThing.Event)} [handler] A handler function previously attached for the event(s)
	 */
	
	/**
	 * register an handler to an event. The handler will be only executed once.
	 * @name one
	 * @memberof EThing
	 * @param {string} event event type string. Multiple space separated events can be given.
	 * @param {function(EThing.Event)} handler the function to be called when the event has been triggered.
	 */
	
	/**
	 * Execute all handlers attached for the given event type.
	 * @name trigger
	 * @memberof EThing
	 * @param {string|EThing.Event} event An event object instance or an event type string.
	 * @param {object} [extraParameters] Additional parameters to pass along to the event handler.
	 */
	
	
	/**
	 * @memberof EThing
	 * @event "ething.resource.removed"
	 */
	 
	/**
	 * @memberof EThing
	 * @event "ething.file.created"
	 */
	 
	/**
	 * @memberof EThing
	 * @event "ething.table.created"
	 */
	 
	/**
	 * @memberof EThing
	 * @event "ething.device.created"
	 */
	 
	/**
	 * @memberof EThing
	 * @event "ething.app.created"
	 */
	/**
	 * authenticated event.
	 *
	 * @memberof EThing
	 * @event "ething.authenticated"
	 */
	
	EventEngine(EThing);
	
	
	EThing.EventEngine = EventEngine;
	
	
})(this);

(function(global) {

	function foreach(arr, handler) {
		if (Array.isArray(arr)) {
			for (var i = 0; i < arr.length; i++) {
				handler(arr[i]);
			}
		}
		else
			handler(arr);
	}

	function D(fn) {
		var status = 'pending',
			doneFuncs = [],
			failFuncs = [],
			progressFuncs = [],
			resultArgs = null,

		tuples = [
				// action, add listener,
				[ "resolve", "done"],
				[ "reject", "fail"],
				[ "notify", "progress"]
			],
			
		promise = {
			done: function() {
				for (var i = 0; i < arguments.length; i++) {
					// skip any undefined or null arguments
					if (!arguments[i]) {
						continue;
					}

					if (Array.isArray(arguments[i])) {
						var arr = arguments[i];
						for (var j = 0; j < arr.length; j++) {
							// immediately call the function if the deferred has been resolved
							if (status === 'resolved') {
								arr[j].apply(this, resultArgs);
							}

							doneFuncs.push(arr[j]);
						}
					}
					else {
						// immediately call the function if the deferred has been resolved
						if (status === 'resolved') {
							arguments[i].apply(this, resultArgs);
						}

						doneFuncs.push(arguments[i]);
					}
				}
				
				return this;
			},

			fail: function() {
				for (var i = 0; i < arguments.length; i++) {
					// skip any undefined or null arguments
					if (!arguments[i]) {
						continue;
					}

					if (Array.isArray(arguments[i])) {
						var arr = arguments[i];
						for (var j = 0; j < arr.length; j++) {
							// immediately call the function if the deferred has been resolved
							if (status === 'rejected') {
								arr[j].apply(this, resultArgs);
							}

							failFuncs.push(arr[j]);
						}
					}
					else {
						// immediately call the function if the deferred has been resolved
						if (status === 'rejected') {
							arguments[i].apply(this, resultArgs);
						}

						failFuncs.push(arguments[i]);
					}
				}
				
				return this;
			},

			always: function() {
				return this.done.apply(this, arguments).fail.apply(this, arguments);
			},

			progress: function() {
				for (var i = 0; i < arguments.length; i++) {
					// skip any undefined or null arguments
					if (!arguments[i]) {
						continue;
					}

					if (Array.isArray(arguments[i])) {
						var arr = arguments[i];
						for (var j = 0; j < arr.length; j++) {
							// immediately call the function if the deferred has been resolved
							if (status === 'pending') {
								progressFuncs.push(arr[j]);
							}
						}
					}
					else {
						// immediately call the function if the deferred has been resolved
						if (status === 'pending') {
							progressFuncs.push(arguments[i]);
						}
					}
				}
				
				return this;
			},

			/*then: function() {
				// fail callbacks
				if (arguments.length > 1 && arguments[1]) {
					this.fail(arguments[1]);
				}

				// done callbacks
				if (arguments.length > 0 && arguments[0]) {
					this.done(arguments[0]);
				}

				// notify callbacks
				if (arguments.length > 2 && arguments[2]) {
					this.progress(arguments[2]);
				}
				
				return this;
			},*/
			
			then: function( /* fnDone, fnFail, fnProgress */ ) {
				var fns = arguments;
				return D( function( newDefer ) {
					
					tuples.forEach(function( tuple, i ) {
						var fn = (typeof fns[ i ] == 'function' ) && fns[ i ];

						// deferred[ done | fail | progress ] for forwarding actions to newDefer
						deferred[ tuple[ 1 ] ]( function() {
							var returned = fn && fn.apply( this, arguments );
							if ( returned && (typeof returned.promise == 'function' ) ) {
								returned.promise()
									.progress( newDefer.notify )
									.done( newDefer.resolve )
									.fail( newDefer.reject );
							} else {
								newDefer[ tuple[ 0 ] + "With" ](
									this === promise ? newDefer.promise() : this,
									fn ? [ returned ] : arguments
								);
							}
						} );
					} );
					fns = null;
				} ).promise();
			},

			promise: function(obj) {
				if (obj == null) {
					return promise;
				} else {
					for (var i in promise) {
						obj[i] = promise[i];
					}
					return obj;
				}
			},

			state: function() {
				return status;
			},

			debug: function() {
				console.log('[debug]', doneFuncs, failFuncs, status);
			},

			isRejected: function() {
				return status === 'rejected';
			},

			isResolved: function() {
				return status === 'resolved';
			}
		},

		deferred = {
			resolveWith: function(context) {
				if (status === 'pending') {
					status = 'resolved';
					var args = resultArgs = (arguments.length > 1) ? arguments[1] : [];
					for (var i = 0; i < doneFuncs.length; i++) {
						doneFuncs[i].apply(context, args);
					}
				}
				return this;
			},

			rejectWith: function(context) {
				if (status === 'pending') {
					status = 'rejected';
					var args = resultArgs = (arguments.length > 1) ? arguments[1] : [];
					for (var i = 0; i < failFuncs.length; i++) {
						failFuncs[i].apply(context, args);
					}
				}
				return this;
			},

			notifyWith: function(context) {
				if (status === 'pending') {
					var args = resultArgs = (arguments.length > 1) ? arguments[1] : [];
					for (var i = 0; i < progressFuncs.length; i++) {
						progressFuncs[i].apply(context, args);
					}
				}
				return this;
			},

			resolve: function() {
				return this.resolveWith(this, arguments);
			},

			reject: function() {
				return this.rejectWith(this, arguments);
			},

			notify: function() {
				return this.notifyWith(this, arguments);
			}
		}

		var obj = promise.promise(deferred);

		if (fn) {
			fn.apply(obj, [obj]);
		}

		return obj;
	}

	D.when = function() {
		if (arguments.length < 2) {
			var obj = arguments.length ? arguments[0] : undefined;
			if (obj && (typeof obj.isResolved === 'function' && typeof obj.isRejected === 'function')) {
				return obj.promise();			
			}
			else {
				return D().resolve(obj).promise();
			}
		}
		else {
			return (function(args){
				var df = D(),
					size = args.length,
					done = 0,
					rp = new Array(size);	// resolve params: params of each resolve, we need to track down them to be able to pass them in the correct order if the master needs to be resolved

				for (var i = 0; i < args.length; i++) {
					(function(j) {
                        var obj = null;
                        
                        if (args[j].done) {
                            args[j].done(function() { rp[j] = (arguments.length < 2) ? arguments[0] : arguments; if (++done == size) { df.resolve.apply(df, rp); }})
                            .fail(function() { df.reject(arguments); });
                        } else {
                            obj = args[j];
                            args[j] = new Deferred();
                            
                            args[j].done(function() { rp[j] = (arguments.length < 2) ? arguments[0] : arguments; if (++done == size) { df.resolve.apply(df, rp); }})
                            .fail(function() { df.reject(arguments); }).resolve(obj);
                        }
					})(i);
				}

				return df.promise();
			})(arguments);
		}
	}
	
	global.EThing = global.EThing || {
		utils: {}
	};
	
	global.EThing.utils.Deferred = D;
	
	
})(this);
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
	
	var Blob = global.Blob || function(){};
	var Buffer = global.Buffer || function(){};
	
	var extend = EThing.utils.extend;
	var isResourceId = EThing.utils.isId;
	var isPlainObject = EThing.utils.isPlainObject;
	
	
	
	
	var ajaxSuccessHandlers = [],
		ajaxCompleteHandlers = [],
		ajaxErrorHandlers = [],
		ajaxSendHandlers = [],
		apiRequestPrefilterHandler = null;
	
	
	EThing.Error = function(json){
		this.name = 'EThing.Error';
		if(typeof json == "string")
			json = {
				message: json
			};
		extend(this, {
			message: 'unknown error'
		}, json);
	}
	EThing.Error.prototype = new Error;
	
	
	// only absolute url will be preserved untouched,
	// else api server url is prepended
	EThing.toApiUrl = function(url, auth){
		url = url || '';
		
		if(!/^([a-z]+:)?\/\//.test(url)){
			// relative url
			if(!/^\//.test(url) && url)
				url = '/'+url;
			
			url = EThing.config.apiUrl + url;
		}
		
		if(auth && isApiUrl(url)){
			url = _processAuth(url);
			if(typeof apiRequestPrefilterHandler == 'function')
				url = apiRequestPrefilterHandler(url);
		}
		return url;
	}
	
	// returns true if it is an URL to the HTTP API
	var isApiUrl = function(url){
		return (new RegExp('^([a-z]+:)?//'+EThing.config.apiUrl.replace(/^([a-z]+:)?\/\//,''))).test(url);
	}
	
	
	
	EThing.apiUrl = function(){
		return EThing.toApiUrl();
	}
	
	
	
	var ajax = function(options){
		var deferred = new EThing.utils.Deferred(),
			xhr = new global.XMLHttpRequest();
		
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
			dataType: null, // The type of data that you're expecting back from the server (json -> {object}, text -> {string} , arraybuffer, blob -> (not available on nodejs), buffer (nodejs only) )
			converter: null, // a user defined function to convert the receive data into something else ...
			synchronous: false
		},options);
		
		
		if(typeof options.url != 'string')
			return null;
		
		var url = EThing.toApiUrl(options.url);
		var apiRequest = isApiUrl(url);
		
		
		options.method = options.method.toUpperCase();
		
		var context = options.context || EThing;
		
		var isBodyRequest = !/^(?:GET|HEAD)$/.test( options.method ),
			body = undefined,
			hasData = typeof options.data != 'undefined' && options.data !== null;
		
		
		
		// If data is available, append data to url
		if ( !isBodyRequest && hasData ){
			// GET, HEAD request, append the data to the query string
			url += ( /\?/.test( url ) ? "&" : "?" ) + ( typeof options.data == 'string' ? options.data : EThing.utils.param(options.data));
		}
		
		
		xhr.open(options.method, url, !options.synchronous);
		
		
		// user headers
		var requestContentType = null;
		if(isPlainObject(options.headers)){
			for(var i in options.headers){
				if(options.headers.hasOwnProperty(i)){
					if(/^content-type$/i.test(i)){
						requestContentType = options.headers[i];
					}
					xhr.setRequestHeader(i, options.headers[i]);	
				}
			}
		}
		
		// content-type header
		if(!requestContentType && options.contentType)
			xhr.setRequestHeader('Content-Type', requestContentType = options.contentType);
		
		if(isBodyRequest && hasData){
			
			if(requestContentType){
				
				body = options.data;
				
				if(isPlainObject(options.data) || Array.isArray(options.data)){
					// transform the data according to the content-type
					if(/json/i.test(requestContentType))
						body = JSON.stringify(options.data)
					else if(/application\/x-www-form-urlencoded/i.test(requestContentType))
						body = EThing.utils.param(options.data);
				}
				
			} else {
				// no content-type set, set to defaults
				if(options.data instanceof Blob){
					xhr.setRequestHeader('Content-Type', requestContentType = options.data.type);
					body = options.data;
				} else if( (options.data instanceof ArrayBuffer) || (options.data instanceof Buffer) ){
					xhr.setRequestHeader('Content-Type', requestContentType = 'application/octet-stream');
					body = options.data;
				} else {
					xhr.setRequestHeader('Content-Type', requestContentType = 'application/x-www-form-urlencoded; charset=UTF-8');
					body = typeof options.data == 'string' ? options.data : EThing.utils.param(options.data);
				}
			}
			
		}
		
		
		
		// authentication
		if(apiRequest){
			xhr = _processAuth(xhr);
			if(typeof apiRequestPrefilterHandler == 'function')
				xhr = apiRequestPrefilterHandler(xhr);
		}
		
		// responseType
		var dataType = options.dataType;
		if(dataType && dataType != 'auto') xhr.responseType = dataType;
		
		function reject(error){
			
			var ct = xhr.getResponseHeader("Content-Type") || '',
				data = null;
			
			if(typeof error != 'undefined'){
				data = error;
			}
			else if(/json/.test(ct) || /text\/plain/.test(ct)){
				
				
				switch(xhr.responseType){
					
					case '':
					case 'text':
					case 'json':
						data = xhr.response;
						break;
					case 'blob':
						
						if(options.synchronous){
							
							if(!FileReaderSync){
								throw new Error("FileReaderSync not supported.");
							}
							
							var fileReader = new FileReaderSync();
							data = String.fromCharCode.apply(null, new Uint8Array(fileReader.readAsArrayBuffer(xhr.response)));
						} else {
							data = EThing.utils.Deferred();
							
							if(!FileReader){
								throw new Error("FileReaderSync not supported.");
							}
							
							var fileReader = new FileReader();
							fileReader.onload = function() {
								data.resolve( String.fromCharCode.apply(null, new Uint8Array(this.result)) );
							};
							fileReader.readAsArrayBuffer(xhr.response);
						}
						
						break;
					case 'arraybuffer':
						data = String.fromCharCode.apply(null, new Uint8Array(xhr.response));
						break;
					case 'buffer':
						data = xhr.response.toString("utf8");
						break;
					default:
						throw new Error(xhr.responseType+" response type not supported.");
						break;
				}
				
			}
			
			EThing.utils.Deferred.when(data).always(function(data){
				
				try{
					data = JSON.parse(data);
				} catch(e){}
				
				var error = new EThing.Error(data || (xhr.status ? (xhr.status+' ['+xhr.statusText+']') : 'unknown error')),
					args = [error,xhr,options];
				
				EThing.trigger('ething.request.error',args);
				ajaxErrorHandlers.forEach(function(handler){
					handler.apply(context,args);
				});
				EThing.trigger('ething.request.complete',args);
				ajaxCompleteHandlers.forEach(function(handler){
					handler.apply(context,args);
				});
				deferred.rejectWith(context,args);
				
			});
			
			
		}
		
		function resolve(data){
			var args = [data,xhr,options];
			
			EThing.trigger('ething.request.success',args);
			ajaxSuccessHandlers.forEach(function(handler){
				handler.apply(context,args);
			});
			EThing.trigger('ething.request.complete',args);
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
				var data = xhr.response;
				
				if(dataType == 'auto'){
					if(/json/.test(xhr.getResponseHeader("Content-Type") || '')){
						try {
							data = JSON.parse(data);
						} catch(err){}
					}
				} else if(dataType == 'json' && typeof data === 'string'){ // for ie compatibility
					try {
						data = JSON.parse(data);
					} catch(err){}
				}
				
				if(typeof options.converter == 'function'){
					data = options.converter.call(context,data,xhr,options);
				}
				
				resolve(data);
			}
			else
				reject();
		}
		xhr.onerror=function(){reject();};
		xhr.onabort=function(){reject();};
		xhr.onprogress=function(e){
			deferred.notifyWith(context,[e,xhr,options]);
		}
		
		var evt = EThing.Event('ething.request.send');
		EThing.trigger(evt,[xhr, options]);
		
		if(evt.isDefaultPrevented()){
			reject('Aborded');
		}
		else {
		
			ajaxSendHandlers.forEach(function(handler){
				handler.call(context,xhr);
			});
			
			xhr.send(body);
			
		}
		
		return deferred.promise();
	}
	
	function isResourceMetaData(json){
		return json.hasOwnProperty('id') && json.hasOwnProperty('type') && json.hasOwnProperty('name');
	}
	
	var getClass = EThing.getClass = function (str){
		var cc = str.split(/[.\\]/), obj = EThing;
		cc.forEach(function(c){
			if(typeof obj[c] != 'undefined')
				obj = obj[c];
			else {
				obj = undefined;
				return false;
			}
		});
		return obj;
	}
	
	var instanciate = EThing.instanciate = function (json){
		var cl = getClass(json.type);
		return cl ? new (cl)(json) : false;
	}
	
	// if the argument is a json object describing a resource, then it converts it into a Resource instance, else it returns the object unchanged
	EThing.resourceConverter = function(data, xhr){
		
		if(typeof data == 'object' && data !== null){
			
			var isArray = Array.isArray(data);
			if(!isArray) data = [data];
			
			// convert into resource instance
			data = data.map(function(r){
				return EThing.instanciate(r);
			}).filter(function(r){
				return r;
			});
			
			
			// update the arbo collection with the new properties
			// and return the corresponding resource object(s)
			data = EThing.arbo.update(data).resources;
			
			if(!isArray) data = data.length ? data[0] : null;
		}
		
		return data;
	}
	
	
	
	
	/**
	 * Make a HTTP request. The options object contains the following properties :
	 *  - url {string} __required__ The url of the request. The API url will be prepended to relative URLs.
	 *  - method {string} The HTTP request method to use. Default is GET.
	 *  - data {string|object|Blob|ArrayBuffer|Buffer} The query string for GET request. The HTTP request body for POST|PATCH|PUT requests. If an object is given, it will be serialized into a query string.
	 *  - contentType {string} When sending data to the server, use this content type. Default is 'application/octet-stream' if the data is an instance of ArrayBuffer or Buffer, if data is an instance of Blob, the default will be the type of the data itself, else 'application/x-www-form-urlencoded; charset=UTF-8'.
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
	 *   url: '/files/'+fileId,
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
		
		if(typeof callback == 'function') {
			d.always(function(){
				callback.apply(this,Array.prototype.slice.call(arguments));
			});
		}
		
		// if sync return the result instead of the deferred object !
		if(opt.synchronous){
			var result = null;
			d.always(function(r){
				result = r;
			});
			return result;
		} else {
			return d;
		}
	}
	
	
	/**
	*
	*/
	EThing.apiRequestPrefilter = function(handler){
		apiRequestPrefilterHandler = handler;
	}
	/**
	 * Register a handler to be called just before API requests is sent.
	 *
	 * @method EThing.ajaxSend
	 * @param {function(XHR)} handler The function to be invoked.
	 */
	EThing.ajaxSend = function(handler){
		if(typeof handler == 'function'){
			ajaxSendHandlers.push(handler);
		}
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
	var DeferredObject = EThing.DeferredObject = function(){
		
		var resolvedDfr = EThing.utils.Deferred().resolve(),
			queue = [],
			self = this;
		
		
		['done','fail','always','progress','then','state','isRejected','isResolved'].forEach(function(fctname){
			this[fctname] = function(){
				// get last deferred object in queue
				var dfr = queue.length ? queue[queue.length-1].dfr : resolvedDfr;
				
				var r = dfr[fctname].apply(self,Array.prototype.slice.call(arguments));
				
				if(typeof r == 'object' && fctname!=='then'){
					// dfr object
					return self;
				} else {
					return r; // state , isRejected, isResolved, then
				}
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
							
							// why ? I don't remember ...
							/*if(args.length>0 && (args[0] instanceof EThing.Resource) && args[0].id() === self.id() )
								self._fromJson(args[0].json()); // update resource metadata*/
							
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

	
	
	
	
	/*
	* Configuration
	*/
	
	var defaultApiUrl = (global.location ? (window.location.protocol+'//'+window.location.hostname) : 'http://localhost')+'/ething/api';
	
	
	
	EThing.config = extend({
		apiUrl: defaultApiUrl,
	},EThing.config);
	
	
	
	
	
	
	
	
	
	
	
	
	
	

	/**
	 * Base class of all the resources
	 * @protected
	 * @class
	 * @memberOf EThing
	 * @param {object} json
	 */
	EThing.Resource = function (json)
	{
		DeferredObject.call(this);
		
		EThing.EventEngine(this);
		
		this._fromJson(json, true);
	}
	EThing.utils.inherits(EThing.Resource,DeferredObject);
	
	// loader
	EThing.Resource.prototype._fromJson = function(json, noTrigger){
		
		var updated = this._json && json && this._json.modifiedDate && json.modifiedDate && this._json.modifiedDate !== json.modifiedDate;
		var updatedKeys = [];
		
		json = extend({
			name:null,
			id:null,
			type:null,
			createdBy:null,
			createdDate: 0,
			modifiedDate: 0,
			data: null,
			description: null
		}, json || {});
		
		if(!noTrigger && updated) {
			// list the kays that have been updated
			Object.keys(json).forEach(function(key){
				if((typeof this._json[key] === 'undefined') || !EThing.utils.isEqual(json[key],this._json[key])){
					updatedKeys.push(key);
				}
			},this);
		}
		
		this._json = json;
		
		if(!noTrigger && updated) {
			//console.log('resource updated '+this.name());
			this.trigger('updated', [updatedKeys]);
			EThing.trigger('ething.resource.updated',[this, updatedKeys]);
		}
		
		return updated;
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
	 * Returns information about the Resource which creates it.
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {Object|null}
	 */
	EThing.Resource.prototype.createdBy = function(){
		return this._json.createdBy;
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
	 *  Returns the type of this resource :
	 *  - "File"
	 *  - "Table"
	 *  - "App"
	 *  - "Device"
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.baseType = function() {
		return this._json.type.split('\\').shift();
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
	 * Tells if this resource is publicly available.
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {boolean|string}
	 */
	EThing.Resource.prototype.public = function() {
		return this._json.public || false;
	}
	
	/**
	 * Returns the data attached to this resource.
	 * @memberof EThing.Resource
	 * @param {string} [name] an optional attribute name.
	 * @param {} [defaultValue] a default value if the attribute was not found.
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @this {EThing.Resource}
	 * @returns {object|null}
	 */
	EThing.Resource.prototype.data = function(name, defaultValue) {
		if(typeof name == 'undefined')
			return this._json.data;
		else {
			return this._json.data.hasOwnProperty(name) ? this._json.data[name] : defaultValue;
		}
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
	
	// resource modificators (async)
	/**
	 * Remove this resource.
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @param {Boolean} [removeChildren] When true, the children are also removed. Default to false.
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Resource} The instance on which this method was called.
	 * @fires EThing#ething.resource.removed
	 * @example
	 * resource.remove().done(function(){
	 *   // the resource was successfully removed
	 * });
	 */
	EThing.Resource.prototype.remove = function(removeChildren, callback){
		return this.deferred(function(){
				return EThing.Resource.remove(this, callback);
			});
	}
	
	EThing.Resource.prototype.update = function(callback){
		return this.deferred(function(){
				return EThing.get(this, callback);
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
		var args = [].slice.call(arguments);
		return this.deferred(function(){
				args.unshift(this);
				return EThing.Resource.set.apply(EThing, args);
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
	 * 
	 * // you can also write :
	 * resource.setData("key", "value").done(function(){
	 *   // success
	 * });
	 */
	EThing.Resource.prototype.setData = function(data, callback){
		
		if(typeof data === 'string' && typeof callback != 'function'){
			var key = data, value = callback, callback = arguments[2];
			data = {};
			data[key] = value;
		}
		
		return this.set({'data':data},callback);
	}
	
	
	
	
	
	

	
	
	
	
	
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
	EThing.list = EThing.find = function(a,b)
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
			'url': '/resources?' + EThing.utils.param({'q':query}),
			'method': 'GET',
			'dataType': 'json',
			'converter': EThing.resourceConverter
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
			'dataType': 'json',
			'method': 'GET'
		},callback);
	};
	
	
	/*
	Resource,callback
	*/
	EThing.Resource.remove = function(a,removeChildren,callback)
	{
		var context;
		if(a instanceof EThing.Resource){
			context = a;
			a = a.id();
		}
		else if(!isResourceId(a)) {
			throw "First argument must be a Resource object or a Resource id : "+a;
			return;
		}
		
		if(arguments.length==2 && typeof removeChildren === 'function'){
			callback = removeChildren;
			removeChildren = false;
		}
		
		return EThing.request({
			'url': '/resources/' + a + '?' + EThing.utils.param({'children':removeChildren}),
			'method': 'DELETE',
			'context': context
		},callback).done(function(){
			EThing.trigger('ething.resource.removed',[a]);
		});
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
			throw "First argument must be a Resource object or a Resource id : "+a;
			return;
		}
		
		var callback = b;
		
		return EThing.request({
			'url': '/resources/' + a,
			'dataType': 'json',
			'method': 'GET',
			'context': context,
			'converter': EThing.resourceConverter
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
			throw "First argument must be a Resource object or a Resource id : "+a;
			return;
		}
		
		var callback = c;
		
		return EThing.request({
			'url': '/resources/' + a,
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': b,
			'context': context,
			'headers': {
				"X-HTTP-Method-Override": "PATCH"
			},
			'converter': EThing.resourceConverter
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
	* Settings
	*/
	
	EThing.settings = EThing.settings || {};
	
	/**
	 * Retrieve the settings.
	 * @memberof EThing.settings
	 * @this {EThing.settings}
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 */
	
	EThing.settings.get = function(callback){
		return EThing.request({
			'url': '/settings',
			'dataType': 'json',
			'method': 'GET'
		},callback);
	};
	
	/**
	 * Update the settings.
	 * @memberof EThing.settings
	 * @this {EThing.settings}
	 * @param {object} [data] updated settings object
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 */
	EThing.settings.set = function(data, callback){
		
		if(!isPlainObject(data))
			throw "First argument must be an object !";
		
		
		return EThing.request({
			'url': '/settings',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': data,
			'headers': {
				"X-HTTP-Method-Override": "PATCH"
			}
		},callback);
	};
	
	
	
	/**
	 * Send a notification.
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
			'data': query
		},callback);
	}
	
	
	
	
	
	/*
	 * AUTH
	 */
	
	var NoAuth = function(a){ return a; };
	
	
	// private
	var _app = null,
		_device = null,
		_scope = null,
		_authType = null,
		_processAuth = NoAuth; // function(xhr|url) -> return xhr|url
	
	
	
	/**
	 * @namespace EThing.auth
	 */

	EThing.auth = {};
	
	
	
	/**
	 * Returns true if the authentication process has been successful.
	 * @method EThing.auth.isAuthenticated
	 * @returns {boolean}
	 */
	EThing.auth.isAuthenticated = function(){
		return !!_authType;
	}
	
	/**
	 * Returns the authenticated app. Only available with app's apikey authentication.
	 * @method EThing.auth.getApp
	 * @returns {EThing.App} the authenticated app or null.
	 */
	EThing.auth.getApp = function(){
		return _app;
	}
	
	/**
	 * Returns the authenticated app. Only available with devices's apikey authentication.
	 * @method EThing.auth.getDevice
	 * @returns {EThing.Device} the authenticated device or null.
	 */
	EThing.auth.getDevice = function(){
		return _device;
	}
	
	/**
	 * Returns the scope of the current authentication
	 * @method EThing.auth.getScope
	 * @returns {string} the scope. May be an empty string if no permissions is set. May be null if full permissions.
	 */
	EThing.auth.getScope = function(){
		return _scope;
	}
	
	
	
	/**
	 * Reset authentication. You must restart an authentication process to make API calls again.
	 * @method EThing.auth.reset
	 */
	EThing.auth.reset = function(){
		_app = null;
		_device = null;
		_authType = null;
		_scope = null;
		_processAuth = NoAuth;
	}
	
	
	
	
	EThing.auth.setApiKey = function(apiKey){
		
		EThing.auth.reset();
		
		_processAuth = function(xhrOrUrl){
			
			if(typeof xhrOrUrl == 'string')
				xhrOrUrl = EThing.utils.insertParam(xhrOrUrl, 'api_key', apiKey);
			else 
				xhrOrUrl.setRequestHeader('X-API-KEY', apiKey);
			
			return xhrOrUrl;
		};
		
	};
	
	EThing.auth.setBasicAuth = function(login, password){
		
		EThing.auth.reset();
		
		_processAuth = function(xhrOrUrl){
			
			if(typeof xhrOrUrl == 'string')
				xhrOrUrl = xhrOrUrl.replace(/\/\/([^:]+:[^@]+@)?/, '//'+login+':'+password+'@');
			else 
				xhrOrUrl.setRequestHeader("Authorization", "Basic " + global.btoa(login + ":" + password));
			
			return xhrOrUrl;
		};
	};
	
	
	
	
	/**
	 * Initialize the eThing library.
	 *
	 * @method EThing.initialize
	 * @param {Object} options
	 * @param {number} options.apiUrl The URL of your eThing API (e.g. http://example.org/ething/api ).
	 * @param {number} [options.apiKey] Authenticate with an API key.
	 * @param {number} [options.login] Basic Authentication login (Should be used only server side i.e. NodeJS).
	 * @param {number} [options.password] Basic Authentication password (Should be used only server side i.e. NodeJS).
	 * @param {function(EThing.Error)} [errorFn] it is executed on authentication error.
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}
	 * @fires EThing#ething.authenticated
	 * @example
	 *
	 * EThing.initialize({
     *    apiUrl: 'http://example.org/ething/api',
     *    apiKey: 'a4e28b3c-1f05-4a62-95f7-c12453b66b3c'
     *  }, function(){
	 *    // on authentication success
	 *    alert('connected !');
	 *  }, function(error) {
     *    // on authentication error
     *    alert(error.message);
     *  });
	 *
	 */
	EThing.initialize = function(options, successFn, errorFn){
		
		EThing.auth.reset();
		
		options = extend({
			apiUrl: null,
			// auth apikey
			apiKey: null,
			// auth basic
			login: null,
			password:null
		},options || {});
		
		if(options.apiUrl)
			EThing.config.apiUrl = options.apiUrl;
		
		
		if(options.apiKey)
			EThing.auth.setApiKey(options.apiKey);
		else if(options.login && options.password)
			EThing.auth.setBasicAuth(options.login, options.password);
		
		return EThing.request({
			'url': '/auth',
			'dataType': 'json',
			'context': EThing,
			'converter': function(data){
				_authType = data.type;
				if(data.app)
					_app = new EThing.App(data.app);
				if(data.device)
					_device = new EThing.Device.Http(data.device);
				if(data.scope)
					_scope = data.scope;
			}
		}).done(function(){
			
			authenticatedCb_.forEach(function(cb){
				cb.call(EThing);
			});
			
			EThing.trigger('ething.authenticated');
		}).done(successFn).fail(errorFn);
		
	}
	
	
	/**
	 * Register a handler to be executed once the authentication is complete.
	 *
	 * @method EThing.authenticated
	 * @param {function()} callback it is executed on authentication success.
	 *
	 */
	var authenticatedCb_ = [];
	EThing.authenticated = function(callback){
		
		if(typeof callback == 'function'){
			authenticatedCb_.push(callback);
			
			if(EThing.auth.isAuthenticated()){
				callback.call(EThing);
			}
		}
	}
	
	
	
	global.EThing = EThing;
	
})(this);

(function (global) {
	
	var EThing = global.EThing;
	
	
	
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
	EThing.utils.inherits(EThing.File, EThing.Resource);
	
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
	 * Returns the MIME type of this file
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @returns {string}
	 */
	EThing.File.prototype.mime = function(){
		return this._json.mime;
	}
	
	/**
	 * Last time the content of this resource was modified
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @returns {Date}
	 */
	EThing.File.prototype.contentModifiedDate = function() {
		return new Date(this._json.contentModifiedDate);
	}
	
	/**
	 * If this file has a thumbnail (thumbnail is only available for file with MIME type __image/*__), it returns his link, else it returns null.
	 * 
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @param {boolean} [auth=false] wether or not attach any authentication element. Necessary if you are not using {@link EThing.request}.
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
	EThing.File.prototype.thumbnailLink = function(auth) {
	  return this._json.hasThumbnail ? EThing.toApiUrl('files/'+this.id()+'/thumbnail',auth) : null;
	}
	
	/**
	 * Returns the link to access the content.
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @param {boolean} [auth=false] wether or not attach any authentication element. Necessary if you are not using {@link EThing.request}.
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
	EThing.File.prototype.getContentUrl = function(auth) {
		return EThing.toApiUrl('files/'+this.id(),auth);
	}
	
	/**
	 * Returns true if this file has text based content.
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @returns {boolean}
	 */
	EThing.File.prototype.isText = function() {
		return this._json.isText;
	}
	
	/**
	 * Returns true if this file is a script.
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @returns {boolean}
	 */
	EThing.File.prototype.isScript = function() {
		return this._json.isText && this._json.mime === 'application/javascript';
	}
	
	// specific methods
	
	/**
	 * Execute a script file.
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @param {string} [arguments] a string containing the arguments
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.File} The instance on which this method was called.
	 * @example
	 * file.execute().done(function(result){
	 *   // success
	 *   console.log(result);
	 * });
	 *
	 */
	EThing.File.prototype.execute = function(args, callback){
		var args = [].slice.call(arguments);
		return this.deferred(function(){
				args.unshift(this);
				return EThing.File.execute.apply(EThing, args);
			});
	}
	
	/**
	 * Gets the content of this file as text or as binary data.
	 * @memberof EThing.File
	 * @this {EThing.File}
	 * @param {boolean} [binary] if true, return the content as binary data (as Blob in a browser, or Buffer in NodeJs)
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.File} The instance on which this method was called.
	 * @example
	 * file.read().done(function(content){
	 *   // success
	 *   console.log('content as text : '+content);
	 * });
	 * 
	 * // browser :
	 * file.read(true).done(function(contentAsBlob){
	 *   // success
	 * });
	 *
	 * // NodeJs :
	 * var fs = require("fs");
	 * EThing.get('kDO5Fk4').done(function(resource){
	 * 	resource.read(true).done(function(data){
	 * 		// data : Buffer instance
	 * 		fs.writeFile(resource.basename(), data, function(){
	 * 			console.log('It\'s saved!');
	 * 		});
	 * 	});
	 * });
	 *
	 */
	EThing.File.prototype.read = function(binary, callback){
		var args = [].slice.call(arguments);
		return this.deferred(function(){
				args.unshift(this);
				return EThing.File.read.apply(EThing, args);
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
	 * file.write("hello world !").done(function(){
	 *   // success
	 * });
	 *
	 */
	EThing.File.prototype.write = function(data, callback){
		var args = [].slice.call(arguments);
		return this.deferred(function(){
				args.unshift(this);
				return EThing.File.write.apply(EThing, args);
			});
	}
	
	
	
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
	 * @fires EThing#ething.file.created
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
			'url': '/files',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.file.created',[r]);
		});
		
	};
	
	/*
	Resource,boolean,callback{function({string|buffer})}
	*/
	EThing.File.read = function(file, binary, callback)
	{
		var context;
		if(file instanceof EThing.File){
			context = file;
			file = file.id();
		}
		else if(!isResourceId(file)){
			throw "First argument must be a File object or a file id !";
		}
		
		if(typeof callback == 'undefined' && typeof binary == 'function'){
			callback = binary;
			binary = false;
		}
		
		return EThing.request({
			'url': '/files/' + file,
			'method': 'GET',
			'dataType': binary ? (EThing.utils.isNode ? 'buffer' : 'blob') : 'text',
			'context': context
		},callback);
	};
	
	/*
	Resource,args,callback{function({object})}
	*/
	EThing.File.execute = function(file, args, callback)
	{
		var context;
		if(file instanceof EThing.File){
			context = file;
			file = file.id();
		}
		else if(!isResourceId(file)){
			throw "First argument must be a File object or a file id !";
		}
		
		if(typeof callback === 'undefined' && typeof args === 'function'){
			callback = args;
			args = null;
		}
		
		return EThing.request({
			'url': '/files/' + file + '/execute?' + EThing.utils.param({'args':args}),
			'method': 'GET',
			'dataType': 'json',
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
			'url': '/files/' + file_id,
			'dataType': 'json',
			'method': 'PUT',
			'contentType': (typeof b == 'string') ? 'text/plain' : 'application/octet-stream',
			'data': b,
			'context': context,
			'converter': EThing.resourceConverter
		},callback);
	};
	
	
	
	
})(this);
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
			'converter': EThing.resourceConverter
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
			'converter': EThing.resourceConverter
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
			'converter': EThing.resourceConverter
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
			'converter': EThing.resourceConverter
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
			'converter': EThing.resourceConverter
		},callback);
		
	}
	
	
	
})(this);
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
(function (global) {
	
	var EThing = global.EThing;
	
	
	
	
	
	/* private constructor */
	/* base class of device */
	EThing.Device = function(json)
	{
		EThing.Resource.call(this, json);
		
		(this._json.operations || []).forEach(function(operationId){
			if(typeof this[operationId] == 'undefined'){
				var self = this;
				
				this[operationId] = function(data, binary, callback){
					var args = [].slice.call(arguments);
					return this.deferred(function(){
						args.unshift(operationId);
						args.unshift(this);
						return EThing.Device.execute.apply(EThing, args);
					});
				};
				
				this[operationId].getApi = function(callback){
					return EThing.Device.getApi(self, operationId, callback);
				};
				
				this[operationId].executeUrl = function(data){
					return self.executeUrl(operationId, data);
				};
			}
		}, this);
	}
	EThing.utils.inherits(EThing.Device, EThing.Resource);
	
	
	/**
	 * 
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @returns {object|null} Return either an object containing information about the location (coordinates, place, room ...) or null if no location is defined for this device.
	 */
	EThing.Device.prototype.location = function() {
	  return this._json.location || null;
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
	 * List the available operations on this device.
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @returns {string[]}
	 */
	EThing.Device.prototype.operations = function(){
		return this._json.operations ? this._json.operations : [];
	}
	
	
	/**
	 * Execute an operation on this device.
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @param {string} operationId
	 * @param {object} [data] the optional data required by the operation
	 * @param {boolean} [binary] if true, return the content as binary data (as Blob in a browser, or Buffer in NodeJs)
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Device} The instance on which this method was called.
	 * @example
	 * // if this device is a thermometer :
	 * device.execute('getTemperature').done(function(data){
     *   // success, handle the data here
     * });
	 *
	 * // if this device is a switch :
	 * device.execute('setState', {
	 * 	 state: true
	 * });
	 * 
	 * // you may also do :
	 * device.getTemperature().done(function(data){
     *   // success, handle the data here
     * });
	 *
	 */
	EThing.Device.prototype.execute = function(){
		var args = [].slice.call(arguments);
		return this.deferred(function(){
				args.unshift(this);
				return EThing.Device.execute.apply(EThing, args);
			});
	}
	
	/**
	 * Returns an url for executing an operation.
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @param {string} operationId
	 * @param {object} [data] the optional data required by the operation
	 * @returns {string} The url.
	 * @example
	 * 
	 * var image = new Image();
	 * image.src = device.executeUrl('getImage');
	 * document.body.appendChild(image);
	 *
	 */
	EThing.Device.prototype.executeUrl = function(operationId, data){
		var url = 'devices/'+this.id()+'/call/'+operationId;
		
		if(isPlainObject(data) && Object.keys(data).length !== 0){
			var jsonStr = JSON.stringify(data);
			url += '?paramData='+ encodeURIComponent(jsonStr);
		}
		
		return EThing.toApiUrl(url,true);
	}
	
	/**
	 * Retrieve information about a specific operation or all the operations available for this device.
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @param {string} [operationId] if set, only information about this operation will be returned
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Device} The instance on which this method was called.
	 *
	 */
	EThing.Device.prototype.getApi = function(operationId, callback){
		var args = [].slice.call(arguments);
		return this.deferred(function(){
			args.unshift(this);
			return EThing.Device.getApi.apply(EThing, args);
		});
	}
	
	
	
	
	
	/*
	device, operationId[, data ]
	*/
	EThing.Device.execute = function(device, operationId, data, binary, callback){
		
		var context;
		
		if(device instanceof EThing.Device){
			context = device;
			device = device.id();
		}
		else if(isResourceId(device))
			device = device;
		else {
			throw "First argument must be a Device object or a Device id !";
			return;
		}
		
		if(arguments.length == 4){
			
			if(typeof binary == 'function'){
				callback = binary;
				binary = undefined;
			}
			
		} else if(arguments.length == 3){
			
			if(typeof data == 'function'){
				callback = data;
				data = undefined;
			}
			
		}
		
		return EThing.request({
			'url': '/devices/' + device + '/call/' + operationId,
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': typeof data != 'undefined' && data!==null ? JSON.stringify(data) : undefined,
			'dataType': binary ? (EThing.utils.isNode ? 'buffer' : 'blob') : 'auto',
			'context': context
		},callback);
		
	};
	
	
	/*
	device[, operationId]
	*/
	EThing.Device.getApi = function(device, operationId, callback){
		
		var context;
		
		if(typeof operationId == 'function' && typeof callback == 'undefined'){
			callback = operationId;
			operationId = undefined;
		}
		
		if(device instanceof EThing.Device){
			context = device;
			device = device.id();
		}
		else if(isResourceId(device))
			device = device;
		else {
			throw "First argument must be a Device object or a Device id !";
			return;
		}
		
		return EThing.request({
			'url': '/devices/' + device + '/api' + (operationId?('/'+operationId):''),
			'method': 'GET',
			'context': context,
			'dataType': 'json'
		},callback);
		
	};
	
	
	
	
})(this);

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
	EThing.utils.inherits(EThing.Folder,EThing.Resource);
	
	/*
	* Overriding some base methods 
	*/
	
	// find the oldest createdDate
	EThing.Folder.prototype.createdDate = function() {
		var l = this.find(),
			t = null;
		for(var i=0; i<l.length; i++){
			if (t===null || t > l[i].createdDate())
				t = l[i].createdDate();
		}
		return t;
	}
	
	// Find the newest modifiedDate
	EThing.Folder.prototype.modifiedDate = function() {
		var l = this.find(),
			t = null;
		for(var i=0; i<l.length; i++){
			if (t===null || t < l[i].modifiedDate())
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
		
		if(typeof resource === 'string'){
			resource = findOneById(resource);
			if(!resource) return;
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
		lastRefreshTs: 0,
		refresh: function(){
			this.lastRefreshTs = Date.now();
			return refresh.apply(this, Array.prototype.slice.call(arguments));
		},
		remove: remove,
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

(function (global) {
	
	var EThing = global.EThing;
	
	
	
	
	/**
	 * Constructs a Denon Device instance from an object decribing a Denon device (Marantz M-CR611). Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The Denon Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.Denon = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.Denon, EThing.Device);
	
	
	/**
	 * Return the host.
	 * @memberof EThing.Device.Denon
	 * @this {EThing.Device.Denon}
	 * @returns {string}
	 */
	EThing.Device.Denon.prototype.host = function() {
	  return this._json.host;
	}
	
	/**
	 * Return false if the device is not reachable.
	 * @memberof EThing.Device.Denon
	 * @this {EThing.Device.Denon}
	 * @returns {boolean}
	 */
	EThing.Device.Denon.prototype.isReachable = function() {
	  return !!this._json.reachable;
	}
	
	
	
	/**
	 * Creates a new Denon device
	 *
	 * @method EThing.Device.Denon.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.Denon.create({
	 *   name: "Music",
	 *   host: "192.168.1.45"
	 * }).done(function(resource){
	 *     console.log('the new device has been created');
	 * })
	 */
	EThing.Device.Denon.create = function(a,callback){
		
		a.type = 'Denon';
		
		return EThing.request({
			'url': '/devices',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	
	
	
})(this);
(function (global) {
	
	var EThing = global.EThing;
	
	
	/**
	 * Constructs a Http Device instance from an object decribing a http device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The Http Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.Http = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.Http, EThing.Device);
	
	
	/**
	 * 
	 * @memberof EThing.Device.Http
	 * @this {EThing.Device.Http}
	 * @returns {string}
	 */
	EThing.Device.Http.prototype.url = function() {
	  return this._json.url;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.Http
	 * @this {EThing.Device.Http}
	 * @returns {object|null}
	 */
	EThing.Device.Http.prototype.auth = function() {
	  return this._json.auth;
	}
	
	/**
	 * Return the scope of this device.
	 * @memberof EThing.Device.Http
	 * @this {EThing.Device.Http}
	 * @returns {string}
	 */
	EThing.Device.Http.prototype.scope = function() {
	  return (typeof this._json.scope == 'string') ? this._json.scope : '';
	}
	
	/**
	 * Return false if the device is not reachable.
	 * @memberof EThing.Device.Http
	 * @this {EThing.Device.Http}
	 * @returns {boolean}
	 */
	EThing.Device.Http.prototype.isReachable = function() {
	  return !!this._json.reachable;
	}
	
	/**
	 * Make a HTTP request on this device. __Only available if an URL is set__, see {@link EThing.Device#create}
	 * The options are the same as the ones used in {@link EThing.request}.
	 * @memberof EThing.Device.Http
	 * @this {EThing.Device.Http}
	 * @param {string|object} options or an URL
	 * @returns {EThing.Device.Http} The instance on which this method was called.
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
	EThing.Device.Http.prototype.request = function(settings){
		var args = [].slice.call(arguments);
		return this.deferred(function(){
			args.unshift(this);
			return EThing.Device.Http.request.apply(EThing, args);
		});
	}
	EThing.Device.Http.prototype.ajax = EThing.Device.Http.prototype.request;
	
	
	EThing.Device.Http.prototype.getResourceUrl = function(url,auth){
		return EThing.Device.Http.getResourceUrl(this,url,auth);
	}
	
	
	
	
	/**
	 * Set the swagger API specification of this device.
	 * @memberof EThing.Device.Http
	 * @this {EThing.Device.Http}
	 * @param {String|Object} [spec] the swagger API specification.
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Device.Http} The instance on which this method was called.
	 */
	EThing.Device.Http.prototype.setSpecification = function(spec,callback) {
	  if(typeof spec == 'string')
		spec = JSON.parse(spec);
	  return this.set({
		specification: spec
	  },callback);
	}

	/**
	 * Get the swagger API specification of this device.
	 * @memberof EThing.Device.Http
	 * @this {EThing.Device.Http}
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Device.Http} The instance on which this method was called.
	 */
	EThing.Device.Http.prototype.getSpecification = function(callback) {
	  return EThing.Device.Http.getSpecification(this, callback);
	}




	
	
	/**
	 * Creates a new HttpDevice
	 *
	 * @method EThing.Device.Http.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.Http.create({
	 *   name: "foobar",
	 *   url: "123.45.67.89"
	 * }).done(function(resource){
	 *     console.log('the new device can be accessed through : ' + resource.url());
	 * })
	 */
	EThing.Device.Http.create = function(a,callback){
		
		a.type = 'Http';
		
		return EThing.request({
			'url': '/devices',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	
	
	EThing.Device.Http.getResourceUrl = function(device,url,auth){
		if(device instanceof EThing.Device.Http){
			device = device.id();
		}
		
		var o = 'devices/' + device + '/request';
		if( typeof url == 'string'){
			if(!/^\//.test(url))
				url = '/'+url;
			o += url;
		}
		return EThing.toApiUrl(o,auth);
	}
	
	
	/*
	device[, settings ]
	*/
	EThing.Device.Http.ajax = EThing.Device.Http.request = function(a,b){
		
		var devId, context;
		
		if(a instanceof EThing.Device.Http){
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
		
		settings['url'] = EThing.Device.Http.getResourceUrl(devId, settings['url']);
			
		return EThing.request(settings);
		
	};
	
	
	EThing.Device.Http.getSpecification = function(dev, callback){
		var context;
		
		if(dev instanceof EThing.Device.Http){
			context = dev;
			dev = dev.id();
		}
		else if(!EThing.utils.isId(dev))
			throw "First argument must be a Device object or a Device id !";
		
		return EThing.request({
			'url': '/devices/' + dev + '/specification',
			'dataType': 'json',
			'context': context,
			'converter': function(spec){
				if(context instanceof EThing.Device.Http){
					// attach this specification to the device
					context.swaggerSpecification = spec;
				}
				return spec;
			}
		},callback);
		
	};


	
	
})(this);
(function (global) {
	
	var EThing = global.EThing;
	
	
	
	
	/**
	 * Constructs a MQTT Device instance from an object decribing a MQTT device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The MQTT Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MQTT = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MQTT, EThing.Device);
	
	
	/**
	 * 
	 * @memberof EThing.Device.MQTT
	 * @this {EThing.Device.MQTT}
	 * @returns {string}
	 */
	EThing.Device.MQTT.prototype.host = function() {
	  return this._json.host;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MQTT
	 * @this {EThing.Device.MQTT}
	 * @returns {number}
	 */
	EThing.Device.MQTT.prototype.port = function() {
	  return this._json.port;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MQTT
	 * @this {EThing.Device.MQTT}
	 * @returns {object|null}
	 */
	EThing.Device.MQTT.prototype.auth = function() {
	  return this._json.auth || null;
	}
	
	/**
	 * Return true if a connection to the device is opened
	 * @memberof EThing.Device.MQTT
	 * @this {EThing.Device.MQTT}
	 * @returns {boolean}
	 */
	EThing.Device.MQTT.prototype.isConnected = function() {
	  return !!this._json.connected;
	}
	
	
	/**
	 * Set the subscribed topics of this device.
	 * @memberof EThing.Device.MQTT
	 * @this {EThing.Device.MQTT}
	 * @param {String|Array} [subs] the list of the subscribed topics.
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Device.MQTT} The instance on which this method was called.
	 */
	EThing.Device.MQTT.prototype.setSubscription = function(subs,callback) {
	  if(typeof spec == 'string')
		spec = JSON.parse(subs);
	  return this.set({
		subscription: subs
	  },callback);
	}

	/**
	 * Get the subscribed topics of this device.
	 * @memberof EThing.Device.MQTT
	 * @this {EThing.Device.MQTT}
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Device.MQTT} The instance on which this method was called.
	 */
	EThing.Device.MQTT.prototype.getSubscription = function(callback) {
	  return EThing.Device.MQTT.getSubscription(this, callback);
	}
	
	

	
	/**
	 * Creates a new MQTT device
	 *
	 * @method EThing.Device.MQTT.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.MQTT.create({
	 *   host: "localhost",
	 *   topic: "outdoor/thermometer"
	 * }).done(function(resource){
	 *     console.log('the new device has been created');
	 * })
	 */
	EThing.Device.MQTT.create = function(a,callback){
		
		a.type = 'MQTT';
		
		return EThing.request({
			'url': '/devices',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	
	
	EThing.Device.MQTT.getSubscription = function(dev, callback){
		var context;
		
		if(dev instanceof EThing.Device.MQTT){
			context = dev;
			dev = dev.id();
		}
		else if(!EThing.utils.isId(dev))
			throw "First argument must be a Device object or a Device id !";
		
		return EThing.request({
			'url': '/devices/' + dev + '/subscription',
			'dataType': 'json',
			'context': context,
			'converter': function(subs){
				if(context instanceof EThing.Device.MQTT){
					// attach this specification to the device
					context.subscription = subs;
				}
				return subs;
			}
		},callback);
		
	};
	
	
})(this);
(function (global) {
	
	var EThing = global.EThing;
	
	
	
	/**
	 * MySensorsGateway base class constructor.
	 * @protected
	 * @class The MySensorsGateway Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MySensorsGateway = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MySensorsGateway, EThing.Device);
	
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsGateway
	 * @this {EThing.Device.MySensorsGateway}
	 * @returns {boolean}
	 */
	EThing.Device.MySensorsGateway.prototype.isMetric = function() {
	  return this._json.isMetric;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsGateway
	 * @this {EThing.Device.MySensorsGateway}
	 * @returns {string}
	 */
	EThing.Device.MySensorsGateway.prototype.libVersion = function() {
	  return this._json.libVersion;
	}
	
	/**
	 * Return true if a connection to the device is opened
	 * @memberof EThing.Device.MySensorsGateway
	 * @this {EThing.Device.MySensorsGateway}
	 * @returns {boolean}
	 */
	EThing.Device.MySensorsGateway.prototype.isConnected = function() {
	  return !!this._json.connected;
	}
	
	
	/**
	 * Constructs a MySensorsEthernetGateway Device instance from an object decribing a MySensorsEthernetGateway device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The MySensorsEthernetGateway Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MySensorsEthernetGateway = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MySensorsEthernetGateway, EThing.Device.MySensorsGateway);
	
	/**
	 * Returns the IP address of the gateway.
	 * @memberof EThing.Device.MySensorsEthernetGateway
	 * @this {EThing.Device.MySensorsEthernetGateway}
	 * @returns {string}
	 */
	EThing.Device.MySensorsEthernetGateway.prototype.address = function() {
	  return this._json.address;
	}
	
	/**
	 * Constructs a MySensorsSerialGateway Device instance from an object decribing a MySensorsSerialGateway device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The MySensorsGateway Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MySensorsSerialGateway = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MySensorsSerialGateway, EThing.Device.MySensorsGateway);
	
	/**
	 * Returns the Serail port of the gateway.
	 * @memberof EThing.Device.MySensorsSerialGateway
	 * @this {EThing.Device.MySensorsSerialGateway}
	 * @returns {string}
	 */
	EThing.Device.MySensorsSerialGateway.prototype.port = function() {
	  return this._json.port;
	}
	
	/**
	 * Returns the Serail baudrate of the gateway.
	 * @memberof EThing.Device.MySensorsSerialGateway
	 * @this {EThing.Device.MySensorsSerialGateway}
	 * @returns {string}
	 */
	EThing.Device.MySensorsSerialGateway.prototype.baudrate = function() {
	  return this._json.baudrate;
	}
	
	
	
	
	/**
	 * Constructs a MySensorsNode Device instance from an object decribing a MySensorsNode device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The MySensorsNode Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MySensorsNode = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MySensorsNode, EThing.Device);
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsNode
	 * @this {EThing.Device.MySensorsNode}
	 * @returns {string}
	 */
	EThing.Device.MySensorsNode.prototype.nodeId = function() {
	  return this._json.nodeId;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsNode
	 * @this {EThing.Device.MySensorsNode}
	 * @returns {string}
	 */
	EThing.Device.MySensorsNode.prototype.sketchName = function() {
	  return this._json.sketchName;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsNode
	 * @this {EThing.Device.MySensorsNode}
	 * @returns {string}
	 */
	EThing.Device.MySensorsNode.prototype.sketchVersion = function() {
	  return this._json.sketchVersion;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsNode
	 * @this {EThing.Device.MySensorsNode}
	 * @returns {string}
	 */
	EThing.Device.MySensorsNode.prototype.smartSleep = function() {
	  return this._json.smartSleep;
	}
	
	
	
	
	
	/**
	 * Constructs a MySensorsSensor Device instance from an object decribing a MySensorsSensor device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The MySensorsSensor Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MySensorsSensor = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MySensorsSensor, EThing.Device);
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsSensor
	 * @this {EThing.Device.MySensorsSensor}
	 * @returns {string}
	 */
	EThing.Device.MySensorsSensor.prototype.sensorId = function() {
	  return this._json.sensorId;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsSensor
	 * @this {EThing.Device.MySensorsSensor}
	 * @returns {string}
	 */
	EThing.Device.MySensorsSensor.prototype.sensorType = function() {
	  return this._json.sensorType;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsSensor
	 * @this {EThing.Device.MySensorsSensor}
	 * @returns {string}
	 */
	EThing.Device.MySensorsSensor.prototype.val = function(valueType) {
	  return this._json.data.hasOwnProperty(valueType) ? this._json.data[valueType] : null;
	}
	
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsSensor
	 * @this {EThing.Device.MySensorsSensor}
	 * @returns {string}
	 */
	EThing.Device.MySensorsSensor.prototype.setValue = function(valueType, value, callback) {
		var data = {};
		data[valueType] = value;
		return this.setData(data,callback);
	}
	
	
	
	
	
	/**
	 * Creates a new MySensors gateway.
	 *
	 * @method EThing.Device.MySensorsEthernetGateway.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.MySensorsEthernetGateway.create({
	 *   name: "foobar",
	 *   address: "123.45.67.89"
	 * }).done(function(resource){
	 *     console.log('the new MySensors gateway has been added');
	 * })
	 */
	EThing.Device.MySensorsEthernetGateway.create = function(a,callback){
		
		a.type = 'MySensorsEthernetGateway';
		
		return EThing.request({
			'url': '/devices',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	
	/**
	 * Creates a new MySensors gateway.
	 *
	 * @method EThing.Device.MySensorsSerialGateway.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.MySensorsSerialGateway.create({
	 *   name: "foobar",
	 *   port: "/dev/ttyS0",
	 *   baudrate: 115200,
	 * }).done(function(resource){
	 *     console.log('the new MySensors gateway has been added');
	 * })
	 */
	EThing.Device.MySensorsSerialGateway.create = function(a,callback){
		
		a.type = 'MySensorsSerialGateway';
		
		return EThing.request({
			'url': '/devices',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	
	
	/**
	 * Add a new MySensors node to an existing MySensors gateway.
	 *
	 * @method EThing.Device.MySensorsNode.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.MySensorsNode.create({
	 *   name: "node45",
	 *   nodeId: 45,
	 *   gateway: "4ge7r81"
	 * }).done(function(resource){
	 *     // success
	 * })
	 */
	EThing.Device.MySensorsNode.create = function(a,callback){
		
		a.type = 'MySensorsNode';
		
		return EThing.request({
			'url': '/devices',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	
	/**
	 * Add a new MySensors sensor to an existing MySensors node.
	 *
	 * @method EThing.Device.MySensorsSensor.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.MySensorsSensor.create({
	 *   name: "sensor5",
	 *   sensorId: 5,
	 *   node: "h1e7r81"
	 * }).done(function(resource){
	 *     // success
	 * })
	 */
	EThing.Device.MySensorsSensor.create = function(a,callback){
		
		a.type = 'MySensorsSensor';
		
		return EThing.request({
			'url': '/devices',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	
	
	
	
})(this);
(function (global) {
	
	var EThing = global.EThing;
	
	
	
	
	/**
	 * RFLinkGateway base class constructor.
	 * @protected
	 * @class The RFLinkGateway Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.RFLinkGateway = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.RFLinkGateway, EThing.Device);
	
	/**
	 * Returns the inclusion mode state .
	 * @memberof EThing.Device.RFLinkGateway
	 * @this {EThing.Device.RFLinkGateway}
	 * @returns {boolean}
	 */
	EThing.Device.RFLinkGateway.prototype.inclusion = function() {
	  return !!this._json.inclusion;
	}
	
	
	/**
	 * Returns the version number of the firmware.
	 * @memberof EThing.Device.RFLinkGateway
	 * @this {EThing.Device.RFLinkGateway}
	 * @returns {string}
	 */
	EThing.Device.RFLinkGateway.prototype.version = function() {
	  return this._json.version;
	}
	
	/**
	 * Returns the revision number of the firmware.
	 * @memberof EThing.Device.RFLinkGateway
	 * @this {EThing.Device.RFLinkGateway}
	 * @returns {string}
	 */
	EThing.Device.RFLinkGateway.prototype.revision = function() {
	  return this._json.revision;
	}
	
	/**
	 * Returns the build number of the firmware.
	 * @memberof EThing.Device.RFLinkGateway
	 * @this {EThing.Device.RFLinkGateway}
	 * @returns {string}
	 */
	EThing.Device.RFLinkGateway.prototype.build = function() {
	  return this._json.build;
	}
	
	/**
	 * Return true if a connection to the device is opened
	 * @memberof EThing.Device.RFLinkGateway
	 * @this {EThing.Device.RFLinkGateway}
	 * @returns {boolean}
	 */
	EThing.Device.RFLinkGateway.prototype.isConnected = function() {
	  return !!this._json.connected;
	}
	
	
	/**
	 * Constructs a RFLinkSerialGateway Device instance from an object decribing a RFLinkSerialGateway device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The RFLinkGateway Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.RFLinkSerialGateway = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.RFLinkSerialGateway, EThing.Device.RFLinkGateway);
	
	/**
	 * Returns the Serail port of the gateway.
	 * @memberof EThing.Device.RFLinkSerialGateway
	 * @this {EThing.Device.RFLinkSerialGateway}
	 * @returns {string}
	 */
	EThing.Device.RFLinkSerialGateway.prototype.port = function() {
	  return this._json.port;
	}
	
	/**
	 * Returns the Serail baudrate of the gateway.
	 * @memberof EThing.Device.RFLinkSerialGateway
	 * @this {EThing.Device.RFLinkSerialGateway}
	 * @returns {string}
	 */
	EThing.Device.RFLinkSerialGateway.prototype.baudrate = function() {
	  return this._json.baudrate;
	}
	
	
	/**
	 * RFLinkNode base class constructor.
	 * @protected
	 * @class The RFLinkNode Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.RFLinkNode = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.RFLinkNode, EThing.Device);
	
	/**
	 * Returns the protocol used to communicate with this node.
	 * @memberof EThing.Device.RFLinkNode
	 * @this {EThing.Device.RFLinkNode}
	 * @returns {string}
	 */
	EThing.Device.RFLinkNode.prototype.protocol = function() {
	  return this._json.protocol;
	}
	
	/**
	 * Returns the nodeId of this node.
	 * @memberof EThing.Device.RFLinkNode
	 * @this {EThing.Device.RFLinkNode}
	 * @returns {string}
	 */
	EThing.Device.RFLinkNode.prototype.nodeId = function() {
	  return this._json.nodeId;
	}
	
	/**
	 * Returns the switchId of this node (only available for switch/door/motion nodes).
	 * @memberof EThing.Device.RFLinkNode
	 * @this {EThing.Device.RFLinkNode}
	 * @returns {string}
	 */
	EThing.Device.RFLinkNode.prototype.switchId = function() {
	  return this._json.switchId;
	}
	
	/**
	 * Returns the subType of this node.
	 * @memberof EThing.Device.RFLinkNode
	 * @this {EThing.Device.RFLinkNode}
	 * @returns {string}
	 */
	EThing.Device.RFLinkNode.prototype.subType = function() {
	  return this._json.subType;
	}
	
	
	/**
	 * Creates a new RFLink gateway.
	 *
	 * @method EThing.Device.RFLinkSerialGateway.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.RFLinkSerialGateway.create({
	 *   name: "foobar",
	 *   port: "/dev/ttyS0",
	 *   baudrate: 57600,
	 * }).done(function(resource){
	 *     console.log('the new RFLink gateway has been added');
	 * })
	 */
	EThing.Device.RFLinkSerialGateway.create = function(a,callback){
		
		a.type = 'RFLinkSerialGateway';
		
		return EThing.request({
			'url': '/devices',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	
	/**
	 * Creates a new RFLink node. The kinf of node is defined by the mandatory subType attribute.
	 *
	 * @method EThing.Device.RFLinkNode.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.RFLinkNode.create({
	 *   name: "foobar",
	 *   gateway: "4ge7r81",
	 *   subType: "switch", // switch | door | motion | thermometer | weatherStation | multimeter
	 *   protocol: "NewKaku",
	 *   nodeId: "008440e6",
	 *   switchId: "a" // nedded for switch | door | motion
	 * }).done(function(resource){
	 *     console.log('the new RFLink switch has been added');
	 * })
	 */
	EThing.Device.RFLinkNode.create = function(a,callback){
		
		a.type = 'RFLinkNode';
		
		return EThing.request({
			'url': '/devices',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	
	
	
})(this);
(function (global) {
	
	var EThing = global.EThing;
	
	
	
	
	/**
	 * Constructs a RTSP Device instance from an object decribing a RTSP device (typpicaly an IP camera). Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The RTSP Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.RTSP = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.RTSP, EThing.Device);
	
	
	/**
	 * 
	 * @memberof EThing.Device.RTSP
	 * @this {EThing.Device.RTSP}
	 * @returns {string}
	 */
	EThing.Device.RTSP.prototype.url = function() {
	  return this._json.url;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.RTSP
	 * @this {EThing.Device.RTSP}
	 * @returns {string}
	 */
	EThing.Device.RTSP.prototype.transport = function() {
	  return this._json.transport;
	}
	
	/**
	 * Return false if the device is not reachable.
	 * @memberof EThing.Device.RTSP
	 * @this {EThing.Device.RTSP}
	 * @returns {boolean}
	 */
	EThing.Device.RTSP.prototype.isReachable = function() {
	  return !!this._json.reachable;
	}
	
	
	/**
	 * Creates a new RTSP device
	 *
	 * @method EThing.Device.RTSP.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.RTSP.create({
	 *   name: "foobar",
	 *   url: "rtsp://123.45.67.89/stream"
	 * }).done(function(resource){
	 *     console.log('the new device has been created');
	 * })
	 */
	EThing.Device.RTSP.create = function(a,callback){
		
		a.type = 'RTSP';
		
		return EThing.request({
			'url': '/devices',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	

})(this);
(function (global) {
	
	var EThing = global.EThing;
	
	
	
	
	/**
	 * Constructs a SSH Device instance from an object decribing a SSH device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The SSH Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.SSH = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.SSH, EThing.Device);
	
	
	/**
	 * 
	 * @memberof EThing.Device.SSH
	 * @this {EThing.Device.SSH}
	 * @returns {string}
	 */
	EThing.Device.SSH.prototype.host = function() {
	  return this._json.host;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.SSH
	 * @this {EThing.Device.SSH}
	 * @returns {number}
	 */
	EThing.Device.SSH.prototype.port = function() {
	  return this._json.port;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.SSH
	 * @this {EThing.Device.SSH}
	 * @returns {object}
	 */
	EThing.Device.SSH.prototype.auth = function() {
	  return this._json.auth || null;
	}
	
	/**
	 * Return false if the device is not reachable.
	 * @memberof EThing.Device.SSH
	 * @this {EThing.Device.SSH}
	 * @returns {boolean}
	 */
	EThing.Device.SSH.prototype.isReachable = function() {
	  return !!this._json.reachable;
	}
	
	

	
	/**
	 * Creates a new SSH device
	 *
	 * @method EThing.Device.SSH.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.SSH.create({
	 *   host: "localhost",
	 *   auth: {
	 *     user: "foo",
	 *     password: "bar"
	 *   }
	 * }).done(function(resource){
	 *     console.log('the new SSH device has been created');
	 * })
	 */
	EThing.Device.SSH.create = function(a,callback){
		
		a.type = 'SSH';
		
		return EThing.request({
			'url': '/devices',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	
	
	
})(this);
(function (global) {
	
	var EThing = global.EThing;
	
	
	
	/**
	 * Constructs a Yeelight Device instance from an object decribing a Yeelight device. Base class of all Yeelight devices.
	 * @protected
	 * @class The Yeelight Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.Yeelight = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.Yeelight, EThing.Device);
	
	
	/**
	 * Return the host name
	 * @memberof EThing.Device.Yeelight
	 * @this {EThing.Device.Yeelight}
	 * @returns {string}
	 */
	EThing.Device.Yeelight.prototype.host = function() {
	  return this._json.host;
	}
	
	/**
	 * Return true if a connection to the device is opened
	 * @memberof EThing.Device.Yeelight
	 * @this {EThing.Device.Yeelight}
	 * @returns {boolean}
	 */
	EThing.Device.Yeelight.prototype.isConnected = function() {
	  return !!this._json.connected;
	}
	
	
	
	/**
	 * Constructs a YeelightBulbRGBW Device instance from an object decribing a Yeelight LED bulb (color) device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The YeelightBulbRGBW Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.YeelightBulbRGBW = function(json)
	{
		EThing.Device.Yeelight.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.YeelightBulbRGBW, EThing.Device.Yeelight);
	
	
	
	
	
	/**
	 * Creates a new YeelightBulbRGBW device
	 *
	 * @method EThing.Device.YeelightBulbRGBW.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.YeelightBulbRGBW.create({
	 *   host: "192.168.1.125",
	 * }).done(function(resource){
	 *     console.log('the new device has been created');
	 * })
	 */
	EThing.Device.YeelightBulbRGBW.create = function(a,callback){
		
		a.type = 'YeelightBulbRGBW';
		
		return EThing.request({
			'url': '/devices',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	
	
	
})(this);