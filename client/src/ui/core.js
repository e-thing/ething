(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define([
			'require',
			'ething',
			'jquery',
			'json!config.json',
			'form',
			'./formmodal',
			'./event',
			'./scope',
			'./refreshstrategy',
			'./resourcemeta',
			'./pageengine'
		], factory);
    } else {
        // Browser globals
        factory(root.EThing,root.jQuery);
    }
}(this, function (require, EThing, $, config) {
	
	
	var UI = window.UI || {};
	
	UI.config = config;
	
	UI.isTouchDevice = navigator ? (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase())) : false;
	
	UI.isMobile = function(){
		var $el = $('<div>').addClass('hidden-xs');;
		$el.appendTo($('body'));
		
		var isMobile = $el.is(':hidden');
		
		$el.remove();
		return isMobile;
	}
	
	var pad = function(n, width, z) {
		z = z || '0';
		n = n + '';
		return n.length >= width ? n : new Array(width - n.length + 1)
			.join(z) + n;
	}
	
	
	UI.sizeToString = function(s) {
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
	
	UI.dateToString = function(d) {
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
	
	UI.dateDiffToString = function(diffInSec) {
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
	
	
	
	/* helpers */
	
	var supportsAudioPlayback = function(contentType){
	  var audioElement = document.createElement('audio');
	  return !!(audioElement.canPlayType && audioElement.canPlayType(contentType).replace(/no/, ''));
	};
	
	var supportsVideoPlayback = function(contentType){
	  var videoElement = document.createElement('video');
	  return !!(videoElement.canPlayType && videoElement.canPlayType(contentType).replace(/no/, ''));
	};
	
	
	// default opening rules
	
	var openRules = [{
			filter: function(r){
				return r instanceof EThing.Folder;
			},
			url: function(r){
				return 'data?path='+r.id();
			}
		},{
			filter: function(r){
				return r instanceof EThing.App;
			},
			url: function(r){
				return 'app?appid='+r.id();
			}
		},{
			filter: function(r){
				return r instanceof EThing.Table;
			},
			url: function(r){
				return 'table?rid='+r.id();
			}
		},{
			filter: function(r){
				return r instanceof EThing.File && /^image\//.test(r.mime());
			},
			url: function(r){
				return 'image?rid='+r.id();
			}
		},{
			filter: function(r){
				return r instanceof EThing.File && /^video\//.test(r.mime()) && supportsVideoPlayback(r.mime());
			},
			url: function(r){
				return 'video?rid='+r.id();
			}
		},{
			filter: function(r){
				return r instanceof EThing.File && /^audio\//.test(r.mime()) && supportsAudioPlayback(r.mime());
			},
			url: function(r){
				return 'video?rid='+r.id();
			}
		},{
			filter: function(r){
				return r instanceof EThing.File && r.extension() === 'plot';
			},
			url: function(r){
				return 'plot?rid='+r.id();
			}
		},{
			filter: function(r){
				return r instanceof EThing.Device;
			},
			url: function(r){
				return 'device?rid='+r.id();
			}
		},{
			filter: function(r){
				return (r instanceof EThing.File) && r.isText();
			},
			url: function(r){
				return 'editor?rid='+r.id();
			}
	}];
	
	
	function isOpenable(resource){
		for(var i=0; i<openRules.length; i++){
			if(openRules[i].filter(resource))
				return openRules[i];
		}
		return false;
	};
	
	function open(resource, newTab){
		for(var i=0; i<openRules.length; i++){
			if(openRules[i].filter(resource)){
				if(newTab) window.open('#!'+openRules[i].url(resource),'_blank');
				else UI.go(openRules[i].url(resource));
				return true;
			}
		}
		return false;
	};
	
	
	function download(url, filename, callback){
		
		EThing.request({
			url: url,
			dataType: 'blob'
		}).done(function(data){
			require(['filesaver'], function(saveAs){
				saveAs(data, filename);
				if(typeof callback == 'function')
					callback.call(resource);
			});
		})
	};
	
	var actions = [
		{
			name: 'open',
			icon: 'eye-open',
			filter: function(r){
				var i;
				return r instanceof EThing.Resource && (i=isOpenable(r)) && UI.parseUrl(i.url(r)).path !== UI.path();
			},
			fn: open
		},{
			name: 'chart',
			icon: 'stats',
			filter: function(r){
				return r instanceof EThing.Table && 'plot' !== UI.path();
			},
			fn: function(r){
				UI.go('plot',{
					rid: r.id()
				});
			}
		},{
			name: 'edit',
			icon: 'edit',
			filter: function(r){
				return (r instanceof EThing.App) && 'editor' !== UI.path();
			},
			fn: function(r){
				UI.go('editor',{
					rid: r.id()
				});
			}
		},{
			name: 'download',
			icon: 'download',
			filter: function(r){
				return r instanceof EThing.Resource && typeof r.getContentUrl === 'function' && !(r instanceof EThing.App);
			},
			fn: function(r){
				
				if(r instanceof EThing.Table){
					$.FormModal({
						item: new $.Form.FormLayout({
							items: [{
								name: 'format',
								item: new $.Form.Select({
									'JSON': 'json',
									'CSV': 'csv'
								})
							}],
							value: 'json'
						}),
						title: "Format ...",
						validLabel: '+Download'
					},function(props){
						var format = props.format;
						download(r.getContentUrl()+'?fmt='+(format=="json"?"json_pretty":format), r.basename().replace(/\.db$/i,'')+'.'+format);
					});
				}
				else
					download(r.getContentUrl(), r.basename());
			}
		},{
			name: 'settings',
			icon: 'cog',
			filter: function(r){
				return r instanceof EThing.Resource && !(r instanceof EThing.Folder);
			},
			fn: function(r){
				UI.go('resource',{
					rid: r.id()
				});
			}
		},{
			name: 'remove',
			icon: 'trash',
			filter: function(r){
				return true;
			},
			fn: function(r){
				
				function countChildren(resource){
					var children = EThing.arbo.find(function(r){
						return r.createdBy() && r.createdBy().id === resource.id();
					});
					return children.length;
				}
				
				var confirmText, resources = [], hasChildren = false;
				
				if(Array.isArray(r) && r.length==1) r = r[0];
				
				if(r instanceof EThing.Resource){
					confirmText = "Remove the "+ r.type().toLowerCase() + " '" + r.name() + "' definitely ?";
					resources.push(r);
				} else if(Array.isArray(r) && r.length){
					confirmText = "Remove the "+r.length+" selected resource(s) definitely ?"
					resources = r;
				}
				
				for(var i in resources){
					if(countChildren(resources[i])){
						hasChildren = true;
						break;
					}
				}
				
				var $html = $('<div>').html(
					'<p>'+
						confirmText+
					'</p>'
				);
				
				if(hasChildren){
					$html.append(
						'<div class="checkbox">'+
							'<label>'+
								'<input type="checkbox"> Remove also the children resources'+
							'</label>'+
						'</div>'
					);
				}
				
				$html.modal({
					title: 'Removing resources',
					buttons: {
						'!Remove': function(){
							
							var removeChildren = $html.find('input').prop('checked');
							
							resources.forEach(function(r){
								r.remove(removeChildren);
							});
							
						},
						'Cancel': null
					}
				});
				
			}
		}
	];
	
	
	var runAction = function(name, r){
		actions.forEach(function(action){
			if(action.name===name && action.filter(r)){
				action.fn(r);
			}
		});
	};
	
	var imageSquareResizeBlob = function(blob, size, cb){
		var dfr = $.Deferred();
		
		// blob to image conversion
		var imageUrl = (window.URL || window.webkitURL).createObjectURL( blob ),
			image = new Image();
		image.src = imageUrl;
		
		image.onload = function(){
			
			// resize/crop the image
			
			var s = parseInt(Math.min(image.width,image.height)),
				outs=128,
				dx = (image.width - s)/2,
				dy = (image.height - s)/2,
				canvas = document.createElement("canvas"),
				ctx = canvas.getContext("2d");
			
			canvas.width = outs;
			canvas.height = outs;
			ctx.drawImage(image, dx,dy,s,s,0,0,outs,outs);
			
			// convert into blob
			var binary = atob(canvas.toDataURL('image/png').replace('data:image/png;base64,','')),
				array = [];
			for (var i = 0; i < binary.length; i++) {
				array.push(binary.charCodeAt(i));
			}
			
			dfr.resolve( new Blob([new Uint8Array(array)], {type: 'image/png'}) );
		}
		
		return dfr.promise().done(cb);
	};
	
	
	
	UI.rel2abs = function(rel, base){
		var parser = document.createElement('a'), url = '';
		
		if(typeof base != 'string'){
			// current base
			base = location.href;
		}
		
		base = base.replace(/\/[^/]*$/,'');
		
		if(/^([a-z]+:)?\/\//.test(rel)){
			url = rel;
		}
		else if(/^\//.test(rel)){
			parser.href = base;
			url = parser.protocol +'//'+ parser.host + rel;
		}
		else {
			url = base + '/' + rel;
		}
		
		parser.href = url;
		return parser.href;
	}
	
	
	
	
	
	$.extend(true,UI, {
		actions: actions,
		runAction: runAction,
		isOpenable: isOpenable,
		open: open,
		imageSquareResizeBlob: imageSquareResizeBlob
	});
	
	
	
	UI.init = function(callback){
		
		if(UI.initialized===true) return;
		UI.initialized = true;
		
		UI.fillData();
		
		UI.$element = $('body').empty();
		
		if(UI.data.app === 'android'){
			UI.$element.addClass('app-android modal-fullscreen');
		}
		
		if(UI.isTouchDevice)
			UI.$element.addClass('touchOnly');
		
		UI.on('ui-pageChange', function(){
			// remove all modal dialogs of the current view
			$('body>.modal, body>.modal-backdrop').remove();
			$('body').removeClass('modal-open');
		});
		
		$(window).on('hashchange.ui', function(){
			UI.process();
		});
		
		require(['./header', './container', 'css!./default'],function(){
			
			EThing.arbo.load(function(){
				
				console.log('arbo loaded');
				
				UI.startRefresh();
				
				UI.process();
				
				console.log('[UI] init done');
			
				if(typeof callback === 'function')
					callback.call(UI);
				
			});
			
		}, function(){
			UI.$element.html('error');
		});
	};
	
	return UI;
	
}));