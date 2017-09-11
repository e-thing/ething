(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    }
}(this, function ($) {
	
	var UI = window.UI = window.UI || {};
	
	
	
	
	var serialize = function(obj, prefix) {
	  var str = [], p;
	  for(p in obj) {
		if (obj.hasOwnProperty(p)) {
		  var k = prefix ? prefix + "[" + p + "]" : p, v = obj[p];
		  str.push((v !== null && typeof v === "object") ?
			serialize(v, k) :
			encodeURIComponent(k) + "=" + encodeURIComponent(v));
		}
	  }
	  return str.join("&");
	};
	
	
	
	$.extend(true, UI, {
		
		parseUrl : function(url){
			if(typeof url === 'undefined'){
				url = window.location.href.indexOf('#!')===-1 ? '' : window.location.href.replace(/.*#!/,'')
			} else {
				url = url.replace(/^#!/,'');
			}
			var path = url.replace(/(\?|#).*$/,'');
			var query = url.indexOf('?')===-1 ? '' : url.replace(/^[^\?]*\?/,'').replace(/#.*$/,'');
			var hash = url.indexOf('#')===-1 ? '' : url.replace(/^[^#]*#/,'');
			
			var data = {};
			
			if(query.length){
				var vars = query.split('&');
				for (var i = 0; i < vars.length; i++) {
					var pair = vars[i].split('=');
					var key = decodeURIComponent(pair[0]);
					var value = decodeURIComponent(pair[1]);
					if(data.hasOwnProperty(key)){
						// multiple same key
						if(!Array.isArray(data[key])) data[key] = [data[key]];
						data[key].push(value);
					} else {
						data[key] = value;
					}
				}
			}
			
			return {
				path: path,
				query: query, // to be removed ? use data instead
				hash: hash,
				data: data,
				location: url // to be removed ? use UI.buildUrl() instead
			};
		},
		
		buildUrl: function(urlInfo){
			var url = '#!'+(urlInfo.path||'');
			if($.isPlainObject(urlInfo.data) && !$.isEmptyObject(urlInfo.data)){
				url += '?'+serialize(urlInfo.data);
			}
			if(urlInfo.hash) {
				url += '#'+urlInfo.query;
			}
			return url;
		},
		
		path: function(){
			return this.parseUrl().path;
		},
		
		history: [],
		
		go: function(uri, data, hash){
			var d = this.parseUrl(uri);
			
			if($.isPlainObject(data) && !$.isEmptyObject(data)){
				$.extend(true, d.data, data);
			}
			
			if(typeof hash === 'string'){
				d.hash = hash;
			}
			
			window.location.hash = this.buildUrl(d);
		},
		
		/*
		* Set url without changing the history
		*/
		setUrl: function(uri, data, hash){
			var d = this.parseUrl(uri);
			
			if($.isPlainObject(data) && !$.isEmptyObject(data)){
				$.extend(true, d.data, data);
			}
			
			if(typeof hash === 'string'){
				d.hash = hash;
			}
			
			window.history.replaceState("", "", this.buildUrl(d));
		},
		
		goBack: function(){
			if(UI.history.length>1){
				window.history.back();
			} else {
				UI.go(UI.home);
			}
		},
		
		home: 'dashboard',
		
		setTitle: function(title){
			document.title = title;
		},
		
		show404: function(){
			
			UI.error = 404;
			
			require(['pages/error404'], function(pageMain){
				
				pageMain.call(UI);
				
				UI.trigger('ui-error404');
				
			});
			
		},
		
		error: false,
		
		update: false, // true when the page loaded only change by the query string
		
		data: {},
		
		fillData: function(){
			this.data = UI.parseUrl(window.location.href).data;
		}
		
	});
	
	
	
	
	// for debugging
	var dbgEvents = {};
	var compareEventsFromPrevious = function(events, name){
		
		var c = {};
		for(var i in events){
			c[i] = events[i].length
		}
		
		// compare
		var o = dbgEvents[name] || {};
		for(var i in c){
			if(!o[i]) o[i] = 0;
			if(o[i] != c[i]) {
				var d = c[i] - o[i];
				if(d>0) d='+'+d;
				console.log(i+' '+d);
			}
		}
		
		// save
		dbgEvents[name] = c;
	}
	
	
	var cnt = 0;
	
	// hash engine
	
	UI.process = function(force){
		
		var cntCheck = ++cnt;
		
		var url = UI.parseUrl();
		
		if(!url.location){
			UI.setUrl(UI.home);
			url = UI.parseUrl();
		}
		
		var pathjs = 'pages/'+url.path;
		
		if(UI.error === false && !force){
			var previous = UI.history.length ? UI.parseUrl(UI.history[0]) : false;
			
			if(previous !== false && UI.currentPage){
				
				if(previous.location===url.location){
					return; // no change
				} else if(previous.path===url.path && previous.query===url.query){
					
					UI.history.unshift(url.location);
					
					UI.trigger('ui-hashChanged', [url.hash]);
					
					if(typeof UI.currentPage.hashChanged === 'function'){
						UI.currentPage.hashChanged(url.hash);
					}
					
					console.log('page hash changed '+pathjs);
					
					return; // only hash part change, do not go further anyway !
				}
				
				
				if(previous.path === url.path && typeof UI.currentPage.updateView === 'function'){
					// this page accept to be updated !
					
					UI.history.unshift(url.location);
					
					UI.trigger('ui-pageUpdated', [url.data]);
					
					if(typeof UI.currentPage.title === 'function'){
						UI.setTitle( UI.currentPage.title(url.data) );
					}
					
					// update the page, ie: query string change
					UI.currentPage.updateView(url.data);
					
					console.log('page updated '+pathjs);
					
					return;
				}
				
			}
		}
		
		
		// new page ! (or force page reload or this page does not allow update)
		
		// but first remove the current view
		if(UI.currentPage){
			if(UI.currentPage.deleteView()===false && !force){
				// cancel the page change
				UI.setUrl(UI.history[0]);
				return;
			}
		}
		
		
		// now load the new view
		UI.history.unshift(url.location);
		
		UI.currentPage = null;
		UI.error = false;
		
		UI.startRefresh();
		
		UI.trigger('ui-pageChange');
		
		/*console.log('');
		console.log('+-------------------+');
		console.log('|   window events   |');
		console.log('+-------------------+');
		var events = jQuery._data( $(window).get(0), "events" );
		console.log(events);
		console.log('+-------------------+');
		compareEventsFromPrevious(events, 'window');
		console.log('+-------------------+');
		console.log('');*/
		/*console.log('+-------------------+');
		console.log('|  document events  |');
		console.log('+-------------------+');
		console.log(jQuery._data( $(document).get(0), "events" ));
		console.log('+-------------------+');
		console.log('');*/
		
		require([pathjs],function(page){
			if(cntCheck!==cnt) return; // too late !
			
			if(typeof page == 'function' || typeof page == 'string'){
				page = {
					buildView: page
				};
			}
			
			if(typeof page.buildView === 'string'){
				var html = page.buildView;
				page.buildView = function(data){
					UI.Container.set(html);
				};
			}
			
			if(typeof page.deleteView === 'undefined'){
				page.deleteView = function(){};
			}
			
			if(typeof page.title === 'undefined'){
				page.title = url.path;
			}
			
			UI.currentPage = page
			
			// set title
			UI.setTitle(typeof page.title === 'function' ? page.title() : page.title);
			
			// load the view content
			page.buildView(url.data);
			
			console.log('page loaded '+pathjs);
			
			UI.trigger('ui-pageChanged');
			
		}, function(err){
			console.log('unable to load: '+pathjs);
			console.error(err);
			
			if(cntCheck!==cnt) return; // too late !
			
			UI.show404();
		});
		
	};
	
	
	
	
	
	return UI;
	
}));