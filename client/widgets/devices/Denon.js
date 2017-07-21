(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    }
}(this, function ($) {
	
	
	return {
		
		require: ['widget/Widget', 'css!widget/devices/Denon.css'],
		
		instanciate: function(device, options, Widget){
			
			var widget,
				timerId,
				power = false,
				mute = false,
				input = null,
				inputsList = ["CD", "TUNER", "IRADIO", "IPD" ]
			
			var update = function(force){
				
				device.execute('getStatus').done(function(state){
					setPower(!!state.power);
					setInput(state.input);
				});
				
			};
			
			var setPower = function(p){
				power = !!p;
				widget.$element.find('button[data-role="power"]').css('color', power ? '#04ff02' : '#ff0000');
				
				var $btns = widget.$element.find('.d-header-tb button:not([data-role="power"])');
				power ? $btns.removeAttr('disabled') : $btns.attr('disabled','disabled');
			}
			
			var setInput = function(i){
				input = i ? i.toUpperCase() : null;
				
				widget.$element.find('button[data-role="input"] > span.name').text(input || '');
				
				var view = power ? input : 'OFF';
				setView(view);
			}
			
			var setView = function(view){
				
				var $view = widget.$element.find('.d-view'),
					dirtyView = $view.data('view') != view,
					now = + new Date(),
					lastUpdatePeriod = now - ($view.data('t')||0);
				
				$view.data('t', now);
				
				if(dirtyView){
					lastUpdatePeriod = Infinity;
					$view[0].className = $view[0].className.replace(/\bd\-view\-.*?\b/g, '');
					$view.addClass('d-view-'+view);
				}
				
				//console.log(lastUpdatePeriod);
				
				switch(view){
					case 'CD':
						
						if(dirtyView){
							$view.html(
								'<div>'+
									'<div class="d-view-cd-track"></div>'+
									'<div class="d-view-cd-tb btn-group" role="group">'+
										'<button type="button" class="btn btn-default" data-role="prev"><span class="glyphicon glyphicon-step-backward" aria-hidden="true"></span></button>'+
										'<button type="button" class="btn btn-default" data-role="stop"><span class="glyphicon glyphicon-stop" aria-hidden="true"></span></button>'+
										'<button type="button" class="btn btn-default" data-role="pause"><span class="glyphicon glyphicon-pause" aria-hidden="true"></span></button>'+
										'<button type="button" class="btn btn-default" data-role="play"><span class="glyphicon glyphicon-play" aria-hidden="true"></span></button>'+
										'<button type="button" class="btn btn-default" data-role="next"><span class="glyphicon glyphicon-step-forward" aria-hidden="true"></span></button>'+
									'</div>'+
								'</div>'
							);
							
							$view.find('button[data-role="prev"]').click(function(){
								device.execute('setCDControl',{cmd:'PREV_TRACK'}).always(update);
							});
							
							$view.find('button[data-role="stop"]').click(function(){
								device.execute('setCDControl',{cmd:'STOP'}).always(update);
							});
							
							$view.find('button[data-role="pause"]').click(function(){
								device.execute('setCDControl',{cmd:'PAUSE'}).always(update);
							});
							
							$view.find('button[data-role="play"]').click(function(){
								device.execute('setCDControl',{cmd:'PLAY'}).always(update);
							});
							
							$view.find('button[data-role="next"]').click(function(){
								device.execute('setCDControl',{cmd:'NEXT_TRACK'}).always(update);
							});
						}
						
						
						if(lastUpdatePeriod > 5000) device.execute('getCDStatus').done(function(state){
							if($view.data('view') != view) return;
							
							var xml = $($.parseXML(state));
							
							var trackno = parseInt(xml.find('trackno').text());
							var playstatus = xml.find('playstatus').text();
							
							$view.find('.d-view-cd-track').text('track '+trackno);
							
							$view.find('button[data-role]').removeClass('active');
							switch(playstatus){
								case 'STOP':
									$view.find('button[data-role="stop"]').addClass('active');
									break;
								case 'PAUSE':
									$view.find('button[data-role="pause"]').addClass('active');
									break;
								case 'PLAY':
									$view.find('button[data-role="play"]').addClass('active');
									break;
							}
							
						});
						
						break;
					
					case 'NET':
						
						if(dirtyView){
							$view.html(
								'<div>'+
									'<div class="d-view-net-track"></div>'+
									'<div class="d-view-net-artist"></div>'+
								'</div>'
							);
						}
						
						if(lastUpdatePeriod > 5000) device.execute('getNetAudioStatus').done(function(state){
							var xml = $($.parseXML(state));
							
							var track = xml.find('#track').text();
							var artist = xml.find('#artist').text();
							
							$view.find('.d-view-net-track').text(track);
							$view.find('.d-view-net-artist').text(artist);
							
						});
						
						break;
					
					default:
						$view.html('<div class="d-view-default-title">'+view+'<div>');
						break;
				}
				
				$view.data('view',view);
			}
			
			widget = $.extend(Widget(), {
				
				draw: function(){
					
					var $html = $('<div>').html(
						'<div class="d-header">'+
							'<div class="d-header-tb btn-group btn-group-xs" role="group">'+
								'<button type="button" class="btn btn-default" data-role="power"><span class="glyphicon glyphicon-off" aria-hidden="true"></span></button>'+
								'<button type="button" class="btn btn-default" data-role="voldown"><span class="glyphicon glyphicon-volume-down" aria-hidden="true"></span></button>'+
								'<button type="button" class="btn btn-default" data-role="volup"><span class="glyphicon glyphicon-volume-up" aria-hidden="true"></span></button>'+
								'<div class="btn-group btn-group-xs">'+
									'<button type="button" data-role="input" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'+
										'<span class="name"></span> '+
										'<span class="caret"></span>'+
										'<span class="sr-only">Toggle Dropdown</span>'+
									'</button>'+
									'<ul class="dropdown-menu"></ul>'+
								'</div>'+
							'</div>'+
							'<div class="d-header-title"></div>'+
						'</div>'+
						'<div class="d-view"></div>'
					).appendTo(this.$element);
					
					var $inputddl = $html.find('button[data-role="input"]').siblings('.dropdown-menu');
					inputsList.forEach(function(input){
						var $li = $('<li><a href="#">'+input+'</a></li>').click(function(evt){
							evt.preventDefault();
							device.execute('setSource',{
								'src': input
							}).done(function(){
								setInput(input);
							});
						});
						$inputddl.append($li);
					});
					
					$html.find('button[data-role="power"]').click(function(){
						device.execute(power ? 'powerOff' : 'powerOn').always(update);
					});
					
					$html.find('button[data-role="voldown"]').click(function(){
						device.execute('setVolumeDown').always(update);
					});
					
					$html.find('button[data-role="volup"]').click(function(){
						device.execute('setVolumeUp').always(update);
					});
					
					$html.find('.d-header-title').text(device.basename());
					
					timerId = setInterval(function(){
						update();
					}, 15000);
					
					update(true);
				},
				
				destroy: function(){
					clearInterval(timerId);
				}
				
			});
			
			return widget;
			
		}
		
	};
	
	
}));