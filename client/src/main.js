(function (root, factory) {
    if (typeof define === 'function' && define.amd) {


		requirejs.config({
			//baseUrl: "src/lib",
			map: {
				'*': {
					'css': 'require-css/css',
					'text': 'require-text',
					'json': 'require-json'
				},
				'codemirror': { 
					'codemirror/lib/codemirror': 'codemirror' 
				}
			},
			paths: {
				//"js": "..",
				//"ui": "../ui",
				"pages": "../pages",
				"widget": "../widgets",
				"deviceWidget": "../widgets/devices",
				
				'ething' : '../../../js/ething',
				
				'config' : '../../config',
				
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
				'bootstrap-typeahead': '//cdnjs.cloudflare.com/ajax/libs/bootstrap-3-typeahead/4.0.1/bootstrap3-typeahead.min',
				
				'bootstrap-toggle-flat': '//cdnjs.cloudflare.com/ajax/libs/titatoggle/1.2.11/titatoggle-dist-min',
				
				'font-awesome': '//cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min',
				
				'moment': '//cdnjs.cloudflare.com/ajax/libs/moment.js/2.15.1/moment-with-locales.min',
				
				'cronstrue': '//cdn.rawgit.com/bradyholt/cRonstrue/5b4212f2/dist/cronstrue.min',
				
				/*'highstock-lib' : '//code.highcharts.com/stock',
				'highstock' : '//code.highcharts.com/stock/modules/exporting',*/
				'highstock-lib' : 'highcharts',
				'highstock' : 'highcharts/modules/exporting',
				
				'js-beautify': '//cdn.rawgit.com/beautify-web/js-beautify/v1.6.3/js/lib',
				
				'marked': '//cdnjs.cloudflare.com/ajax/libs/marked/0.3.6/marked.min',
				
				'highlight': '//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.5.0/highlight.min',
				'highlight-css': '//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.5.0/styles/github-gist.min',
				
				'filesaver': '//cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2014-11-29/FileSaver.min',
				
				'jquery.gridster': 'jquery.gridster',
				
				'mqttws': '//cdnjs.cloudflare.com/ajax/libs/paho-mqtt/1.0.1/mqttws31',
				
				'urijs': '//cdnjs.cloudflare.com/ajax/libs/URI.js/1.18.12'
				
			},
			
			packages: [{
			  name: "codemirror",
			  location: "//cdnjs.cloudflare.com/ajax/libs/codemirror/5.14.2",
			  main: "codemirror"
			},{
			  name: 'ui',
			  location: '../ui',
			  main: 'core'
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
				
				'imageviewer': ['css!imageviewer'],
				'table': ['css!table'],
				
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
        define(['ething', 'jquery'], factory);
    }
}(this, function (EThing, $) {
	
	
	console.log('loading main.js');
	
	
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
		
		require(['ui'], function(UI){
			$( document ).ready(function(){
				
				EThing.authenticated(function(){
					
					console.log('EThing authenticated');
					
					UI.init();
						
				});
				
			});
		});
		
	}
	else auth();
	
	
	
}));