(function (global) {
	
	var EThing = global.EThing || {
		utils: {}
	};

	var Utils = EThing.utils;
	
	
	Utils.isMobile = (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase()));
	Utils.isTouchDevice = (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase()));
	
	
	
	Utils.isId = function(s){
		return (typeof s == 'string' && /^[0-9a-zA-Z\-_]+$/.test(s));
	}
	
	
	Utils.getParameterByName = function(name) {
		name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
		var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
			results = regex.exec(location.search);
		return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
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
	
	
	var pendingElems = [];
	
	function addPendingElem(elem){
		pendingElems.push(elem);
	}
	function removePendingElem(elem){
		for(var i=0; i<pendingElems.length; i++)
			if(pendingElems[i] === elem){
				pendingElems.splice(i,1);
				i--;
			}
	}
	function isPendingElem(elem){
		for(var i=0; i<pendingElems.length; i++)
			if(pendingElems[i] === elem)
				return true;
		return false;
	}
	function alreadyLoaded(url){
		var dom = [].concat([].slice.call(document.getElementsByTagName("script")),[].slice.call(document.getElementsByTagName("link")));
		var regex = new RegExp('(^|/)'+url.replace( /.*\//, '' )); // not robust
		for(var i=0; i<dom.length; i++){
			if(regex.test(dom[i].src) || regex.test(dom[i].href))
				return dom[i];
		}
		return false;
	}
	
	
	Utils.require = function(urlobj,callback){
		
		var dfr;
		
		if(Array.isArray(urlobj)){
			var deferreds = [];
			
			urlobj.forEach(function(urlobj){
				deferreds.push( Utils.require(urlobj) );
			})
			
			if(deferreds.length)
				dfr = Utils.Deferred.when.apply(Utils.Deferred, deferreds);
		}
		else if(urlobj!==null){
			
			if(typeof urlobj == 'string')
				urlobj = {
					url: urlobj
				};
			
			//console.log(urlobj);
			
			if(!Array.isArray(urlobj.url))
				urlobj.url = [urlobj.url];
			
			if(urlobj.sequential){
				
				var urls = urlobj.url;
				function f(urls){
					return urls.length ? {
						url: [urls.shift()],
						then: f(urls)
					} : null;
				}
				urlobj = f(urls);
			}
			
			
			// inherit the base attribute to the children
			function inherit(obj){
				if(urlobj.base){
					if(Array.isArray(obj))
						obj = obj.map(inherit);
					else if(obj!==null){
						if(typeof obj == 'string')
							obj = {
								url: obj
							};
						if(typeof obj == 'object' && typeof obj.base == 'undefined')
							obj.base = urlobj.base;
					}
				}
				return obj;
			}
			
			var deferreds = [];
			urlobj.url.forEach(function(url){
				
				if(typeof url == 'string'){
					
					// load the script
					var domEl = null, type = null, queue = [];
					
					if(/^[a-z]+!/.test(url)){
						var us = url.indexOf('!');
						type = url.substr(0,us);
						url = url.substr(us+1);
					}
					
					if(urlobj.base && !/^(\/|([a-z]+:)?\/\/)/i.test(url)){
						url = urlobj.base.replace(/\/$/,'') + '/' + url;
					}
					
					if(domEl = alreadyLoaded(url)){
					}
					else {
						if(/\.js$/i.test(url) || type=='js'){
							domEl = document.createElement('script');
							domEl.src = url;
						}
						else if(/\.css$/i.test(url) || type=='css'){
							domEl=document.createElement("link");
							domEl.setAttribute("rel", "stylesheet");
							domEl.setAttribute("type", "text/css");
							domEl.setAttribute("href", url);
						}
						
						if(domEl){
							document.head.appendChild(domEl);
							addPendingElem(domEl);
						}
						
					}
					
					if(domEl){
						var d = new Utils.Deferred();
						
						if(isPendingElem(domEl)){
							domEl.addEventListener('load',function(e){
								removePendingElem(domEl);
								d.resolve();
							})
							domEl.addEventListener('error',function(e){
								removePendingElem(domEl);
								d.reject();
							})
						}
						else {
							d.resolve();
						}
						
						deferreds.push(d);
					}
					
				}
				else if(typeof url == 'object' && url !== null){
					deferreds.push(Utils.require(inherit(url)));
				}
				
			});
			
			
			
			if(deferreds.length){
				dfr = new Utils.Deferred();
				Utils.Deferred.when.apply(Utils.Deferred, deferreds)
					.done(function(){
						// queued urls ?
						if(urlobj.then){
							Utils.require(inherit(urlobj.then)).done(function(){
								dfr.resolve();
							});
						}
						else {
							dfr.resolve();
						}
					})
					.fail(function(){
						dfr.reject();
					});
			}
			
				
			
		}
		
		if(!dfr){
			dfr = new Utils.Deferred();
			dfr.resolve();
		}
		
		return dfr.promise().done(callback);
	}
	
	
	
	Utils.extend = function extend(){
		var args = Array.prototype.slice.call(arguments, 0);
		while(args.length>1){
			var a = args.shift(), b = args.shift();
			for(var key in b)
				if(b.hasOwnProperty(key))
					a[key] = b[key];
			args.unshift(a);
		}
		return args.shift();
	}
	
	
	Utils.isPlainObject = function( obj ) {
		// Not plain objects:
		// - Any object or value whose internal [[Class]] property is not "[object Object]"
		// - DOM nodes
		// - window
		if ( typeof obj !== "object" || obj === null || obj.nodeType || obj === obj.window ) {
			return false;
		}

		if ( obj.constructor &&
				!{}.hasOwnProperty.call( obj.constructor.prototype, "isPrototypeOf" ) ) {
			return false;
		}

		// If the function hasn't returned already, we're confident that
		// |obj| is a plain object, created by {} or constructed with new Object
		return true;
	}
	
	Utils.updateQueryStringParameter = function(uri, key, value) {
		var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
		var separator = uri.indexOf('?') !== -1 ? "&" : "?";
		if (uri.match(re)) {
			return uri.replace(re, '$1' + key + "=" + value + '$2');
		}
		else {
			return uri + separator + key + "=" + value;
		}
	}
	
	
	
	global.EThing = EThing;
	
	
})(this);
