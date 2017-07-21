(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
		
		requirejs.config({
			baseUrl: "lib",
			map: {
				'*': {
					'css': 'require-css',
					'text': 'require-text',
					'json': 'require-json'
				},
				'codemirror': { 
					'codemirror/lib/codemirror': 'codemirror' 
				}
			},
			paths: {
				"js": "..",
				"ui": "../ui",
				"pages": "../pages",
				"widget": "../widgets",
				"deviceWidget": "../widgets/devices",
				
				"jquery": "//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min",
				"jquery-mobile-events": "jquery.mobile.events.min",
				
				'jquery.mousewheel': '//cdnjs.cloudflare.com/ajax/libs/jquery-mousewheel/3.1.13/jquery.mousewheel.min',
				
				"bootstrap": '//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min',
				"bootstrap-css": '//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min',
				
				'bootstrap-select': '//cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.10.0/js/bootstrap-select.min',
				'bootstrap-select-css': '//cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.10.0/css/bootstrap-select.min',
				'bootstrap-toggle': '//gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min',
				'bootstrap-toggle-css': '//gitcdn.github.io/bootstrap-toggle/2.2.2/css/bootstrap-toggle.min',
				'bootstrap-datetimepicker': '//cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.42/js/bootstrap-datetimepicker.min',
				'bootstrap-datetimepicker-css': '//cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.42/css/bootstrap-datetimepicker.min',
				'bootstrap-typeahead': '//cdnjs.cloudflare.com/ajax/libs/bootstrap-3-typeahead/4.0.1/bootstrap3-typeahead',
				
				'bootstrap-toggle-flat': '//cdnjs.cloudflare.com/ajax/libs/titatoggle/1.2.11/titatoggle-dist-min',
				
				'font-awesome': '//cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min',
				
				'moment': '//cdnjs.cloudflare.com/ajax/libs/moment.js/2.15.1/moment-with-locales.min',
				
				
				/*'highstock-lib' : '//code.highcharts.com/stock',
				'highstock' : '//code.highcharts.com/stock/modules/exporting',*/
				'highstock-lib' : 'highcharts',
				'highstock' : 'highcharts/modules/exporting',
				
				'ething' : '../../lib/core',
				
				'js-beautify': '//cdn.rawgit.com/beautify-web/js-beautify/v1.6.3/js/lib',
				
				'marked': '//cdnjs.cloudflare.com/ajax/libs/marked/0.3.6/marked.min',
				
				'highlight': '//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.5.0/highlight.min',
				'highlight-css': '//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.5.0/styles/github-gist.min',
				
				'filesaver': '//cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2014-11-29/FileSaver.min',
				
				'jquery.gridster': 'jquery.gridster'
				
			},
			
			packages: [{
			  name: "codemirror",
			  location: "//cdnjs.cloudflare.com/ajax/libs/codemirror/5.14.2",
			  main: "codemirror"
			}],
			
			shim : {
				
				"bootstrap" : {
					deps :['jquery','css!bootstrap-css']
				},
				"ething": {
					exports: 'EThing'
				},
				
				'form': ['css!form','bootstrap-select','bootstrap-toggle','bootstrap-datetimepicker','bootstrap-typeahead'],
				
				'bootstrap-select': ['css!bootstrap-select-css', 'bootstrap'],
				'bootstrap-toggle': ['css!bootstrap-toggle-css', 'bootstrap'],
				'bootstrap-datetimepicker': ['moment','css!bootstrap-datetimepicker-css', 'bootstrap'],
				
				'highlight': ['css!highlight-css'],
				
				'browser': ['css!browser'],
				'imageviewer': ['css!imageviewer'],
				'resourceselect': ['css!resourceselect'],
				'table': ['css!table'],
				'tableviewer': ['css!tableviewer'],
				'textviewer': ['css!textviewer'],
				
				"highstock": {
					deps :['jquery','highstock-lib/highstock.src'],
					exports: 'Highcharts'
				},
				
				'highcharts/plugin/highcharts-data-deferred': {
					deps: ['highstock']
				},
				
				'jquery.gridster': {
					deps: ['css!jquery.gridster']
				},
				
				'circleBar': {
					deps: ['css!circleBar']
				}
				
			}
			
		});
		
		
        // AMD. Register as an anonymous module.
        root.UI = define(['ething', 'jquery','ui/core'], factory);
    }
}(this, function (EThing, $, UI) {
	
	if(window.UI) return window.UI;
	
	console.log('loading ui.js');
	
	
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
	
	
	window.UI = UI = $.extend(true, UI, {
		
		isTouchDevice : navigator ? (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase())) : false,
		
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
		
		update: false // true when the page loaded only change by the query string
		
	});
	
	//console.log('url:');
	//console.log(UI.parseUrl());
	
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
	
	
	
	UI.init = function(){
		
		if(UI.initialized===true) return;
		UI.initialized = true;
		
		if(UI.isTouchDevice)
			$('body').addClass('touchOnly');
		
		$(window).on('hashchange.ui', function(){
			UI.process();
		});
		
		UI.process();
	}
	
	
	/*
	*
	* START OF THE PROGRAM
	*
	*/
	
	function auth(){
		window.location.replace('../session/login?redirect_uri='+encodeURIComponent(window.location.href));
	}
	
	
	// sanitize and set the server URL and client URL
	var parser = document.createElement('a');
	parser.href = '.';
	var clientUrl = parser.href.replace(/\/$/,'');
	parser.href = '../api';
	var apiUrl = parser.href.replace(/\/$/,'');
	
	
	
	
	
	function getCookie(name) {
	  var value = "; " + document.cookie;
	  var parts = value.split("; " + name + "=");
	  if (parts.length == 2) return parts.pop().split(";").shift();
	}
	
	var csrf_token = getCookie('Csrf-token');
	
	if(csrf_token){
		
		
		// on unauthenticated request, start the auth process
		EThing.ajaxError(function(err,xhr,opt){
			//console.log(err,xhr,opt);
			if(opt.url && /\/devices\/[^\/]+\/call/.test(opt.url)) return;
			if(xhr.status == 401 || xhr.status == 403){
				auth()
			}
		});
		
		EThing.apiRequestPrefilter(function(xhrOrUrl){
			if(typeof xhrOrUrl == 'string'){
				// insert query param
				xhrOrUrl += xhrOrUrl.indexOf('?') !== -1 ? '&' : '?';
				xhrOrUrl += 'csrf_token='+encodeURIComponent(csrf_token);
			} else 
				xhrOrUrl.setRequestHeader('X-Csrf-Token',csrf_token);
			
			return xhrOrUrl;
		});
		
		EThing.initialize({
			apiUrl: apiUrl
		}).fail(auth);
		
		
		
		
		$( document ).ready(function(){
			
			//Dom ready
			ready = true;
			
			UI.$element = $('body');
			
			// event engine
			['on','off','one','trigger'].forEach(function(fn){
				UI[fn] = function(){
					return UI.$element[fn].apply(UI.$element, Array.prototype.slice.call(arguments));
				};
			});
			
			
			require(['ui/header', 'ui/container', 'css!js/ui'],function(){
				
				console.log('ui loaded');
				
				// load the page
				EThing.authenticated(function(){
					
					console.log('EThing authenticated');
					
					if(!window.UI.refreshIntervalId){
						window.UI.refreshIntervalId = setInterval( function(){
							EThing.arbo.refresh(); // refresh the arbo every minute
						}, 60000);
					}
					
					EThing.arbo.load(function(){
						
						console.log('arbo loaded');
						
						UI.init();
						
					});
				});
				
			});
			
		});
		
		
	}
	else auth();
	
	
	
	
	window.UI = UI;
	
	return UI;
	
}));