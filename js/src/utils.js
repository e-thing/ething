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
