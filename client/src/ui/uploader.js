(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','ething','./core','css!./uploader','bootstrap'], factory);
    }
}(this, function ($, EThing, UI) {
	
	
	var Uploader = {
		
		upload: function(file, dir, cb){
			
			if(Array.isArray(file)){
				var dfrs = [];
				for(var i=0; i<file.length; i++)
					dfrs.push(Uploader.upload(file[i],dir));
				return $.when.apply($, dfrs).done(cb);
			}
			
			if(!file || !file.name)
				return;
			
			var d = $.Deferred(),
				fr = new FileReader();
			
			d.done(cb);
			
			fr.onload = function(){
				
				// transform the result into base64 string
				var binary = '',
					bytes = new Uint8Array(fr.result);
				for (var i = 0; i < bytes.byteLength; i++) {
					binary += String.fromCharCode( bytes[ i ] );
				}
				
				var b64data = window.btoa(binary),
					name = file.name;
				
				if(dir instanceof EThing.Folder && dir.name().length)
					name = dir.name()+'/'+name;
				else if(typeof dir === 'string'){
					dir = dir.replace(/\/+$/,'');
					if(dir.length)
						name = dir+'/'+name;
				}
				
				var dfr = EThing.File.create({
					'name': name,
					'content': b64data
				}).done(function(r){
					// the creation was successful
					d.resolve(r,file);
				});
				
				Uploader.UI.add(file.name,dfr);
				
			};
			
			fr.onerror = function(e){
				d.reject(file);
			};
			
			fr.readAsArrayBuffer(file);
			
			return d.promise();
		},
		
		UI:{
			
			build: function(){
				var $html = $('<div id="uploader">'),
					$header = $('<div class="uploader-header">'),
					$body = $('<div class="uploader-body">');
				
				$header.append(
					'<span class="uploader-header-title"></span>',
					$('<span class="uploader-header-close glyphicon glyphicon-remove" aria-hidden="true"></span>').click(function(){
						Uploader.UI.close();
					}).hide()
				);
				
				$html.append($header,$body).appendTo(UI.$element);
				
				return $html;
			},
			close: function(){
				$('#uploader').remove();
			},
			update: function(){
				
				var items = 0, done = 0, fail = 0, uploading = 0, title = "";
				$('.uploader-item','#uploader').each(function(){
					var state = $(this).data('state');
					items++;
					switch(state){
						case 'done':
							done++;
							break;
						case 'fail':
							fail++;
							break;
						case 'uploading':
							uploading++;
							break;
					}
				});
				
				if(uploading)
					title = 'Uploading '+uploading+' item'+(uploading>1?'s':'');
				else
					title = items+' upload'+(uploading>1?'s':'')+' complete';
				
				var $ui = $('#uploader');
				
				$('.uploader-header-title',$ui).html(title);
				$('.uploader-header-close',$ui).toggle(!uploading);
				
			},
			add: function(name,deferred){
				var $ui = $('#uploader');
				if(!$ui.length)
					$ui = Uploader.UI.build();
				
				var $item = $('<div class="uploader-item">'),
					$state = $('<div class="uploader-item-state">'),
					$progress = $('<div class="uploader-item-progress"><div></div></div>'),
					hasProgress = false;
				
				$item.append(
					'<span class="uploader-item-name">'+name+'</span>',
					$state.html('<span class="glyphicon glyphicon-refresh glyphicon-animate"></span>')
				).appendTo($ui.children('.uploader-body'));
				
				$item.data('state','uploading');
				
				Uploader.UI.update();
				
				deferred.progress(function(evt){
					if(evt.lengthComputable){
						var ratio = Math.round(evt.loaded / evt.total);
						$('div',$progress).css('width',ratio+'%');
						if(!hasProgress){
							$state.html($progress);
							hasProgress = true;
						}
					}
				});
				
				deferred.done(function(){
					$state.html('<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>');
					$item.data('state','done');
					$item.addClass('uploader-item-done');
				});
				
				deferred.fail(function(){
					$state.html('<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>');
					$item.data('state','fail');
					$item.addClass('uploader-item-fail');
				});
				
				deferred.always(function(){
					Uploader.UI.update();
				});
				
				
			}
			
		}
		
	};
	
	
	
	UI.Uploader = Uploader;
	
	
	return Uploader;
}));