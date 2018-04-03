(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ui/widget'], factory);
    }
}(this, function ($, Widget) {
	
	
	return {
		
		instanciate: function(sensor){
			
			var minIntervalMs = 500;
			
			
			var widget = Widget({
				title: sensor.basename()
			});
			
			return $.extend({}, widget, {
				
				draw: function(){
					var self = this;
					
					widget.draw.call(this);
					
					this.$element.empty().append(
				
						$('<div>').append(
							'<svg class="state" width="40" height="40" viewBox="0 0 512 512"><g><path d="m338.6,136.1c-23.6-22.7-54.6-34.4-87.4-33.2-62.9,2.5-114.2,55.7-114.4,118.7-0.1,27.9 9.7,55.1 27.6,76.5 25.8,31 40,70.1 40,110.2 0,0-2.7,18.4 10.4,18.4h82.4c13.4,0 10.4-18.4 10.4-18.4 0-39.2 14.4-78 41.7-112.2 16.9-21.3 25.9-46.9 25.9-74.1 0-32.7-13-63.3-36.6-85.9zm-5.6,147c-29.7,37.2-45.6,79.6-46.2,122.8h-61.6c-0.6-44.1-16.4-87-44.8-121.1-14.7-17.7-22.8-40.1-22.7-63.1 0.2-52 42.5-95.9 94.4-98 27.1-1 52.7,8.7 72.1,27.4 19.5,18.7 30.2,43.9 30.2,70.9-0.1,22.5-7.4,43.6-21.4,61.1z"/><path d="m393.2,67.8c-4.1-4.1-10.7-4.1-14.7,0l-25.4,25.4c-4.1,4.1-4.1,10.7 0,14.7s10.7,4.1 14.7,0l25.4-25.4c4.1-4 4.1-10.6 0-14.7z"/><path d="m297.6,440.9h-83.2c-5.8,0-10.4,4.7-10.4,10.4 0,5.8 4.7,10.4 10.4,10.4h83.2c5.8,0 10.4-4.7 10.4-10.4 0-5.7-4.7-10.4-10.4-10.4z"/><path d="m281.9,480.1h-51.7c-5.8,0-10.4,4.7-10.4,10.4 0,5.8 4.7,10.4 10.4,10.4h51.7c5.8,0 10.4-4.7 10.4-10.4 5.68434e-14-5.7-4.7-10.4-10.4-10.4z"/><path d="M256,67.7c5.8,0,10.4-4.7,10.4-10.4V21.4c0-5.8-4.7-10.4-10.4-10.4s-10.4,4.7-10.4,10.4v35.9    C245.6,63.1,250.2,67.7,256,67.7z"/><path d="m158.9,108c4.1-4.1 4.1-10.7 0-14.7l-25.4-25.4c-4.1-4.1-10.7-4.1-14.7,0s-4.1,10.7 0,14.7l25.4,25.4c4.1,4 10.7,4 14.7,0z"/><path d="m439.6,194.6h-35.9c-5.8,0-10.4,4.7-10.4,10.4s4.7,10.4 10.4,10.4h35.9c5.8,0 10.4-4.7 10.4-10.4s-4.7-10.4-10.4-10.4z"/><path d="m108.3,194.6h-35.9c-5.8,0-10.4,4.7-10.4,10.4s4.7,10.4 10.4,10.4h35.9c5.8,0 10.4-4.7 10.4-10.4s-4.6-10.4-10.4-10.4z"/></g></svg>',
							'<span class="loader glyphicon glyphicon-refresh glyphicon-animate" aria-hidden="true" style="display:none;"></span>',
							'<span class="error" style="display:none;">error</span>'
						).css({
							'text-align': 'center',
							'padding': '0 10px'
						})
					).attr('style','display: -webkit-box;display: -moz-box;display: -ms-flexbox;display: -webkit-flex;display: flex;').css({
						'display': 'flex',
						'-webkit-flex-direction': 'column',
						'-moz-flex-direction': 'column',
						'-ms-flex-direction': 'column',
						'-o-flex-direction': 'column',
						'flex-direction': 'column',
						'justify-content': 'center'
					});
					
					
					
					this.$element.find('svg.state').css({
						'cursor': 'pointer'
					}).click(function(){
						
						if(self.isOn()){
							self.async(self.turnOff().done(function(){
								self.setState(false);
							}));
						} else {
							self.async(self.turnOn().done(function(){
								self.setState(true);
							}));
						}
						
					});
					
					this.resourceUpdateFn = function(evt,updatedKeys){
						if(updatedKeys.indexOf('data')!==-1) self.updateState();
					};
					
					sensor.on('updated', this.resourceUpdateFn);
					
					self.updateState();
					
				},
				
				isOn: function(){
					return !!this.state;
				},
				
				turnOn: function(){
					var self = this;
					return sensor.execute('on');
				},
				
				turnOff: function(){
					return sensor.execute('off');
				},
				
				async: function(dfr){
					var $loader = this.$element.find('span.loader');
					var $state = this.$element.find('svg.state');
					
					$state.hide();
					$loader.show();
					
					dfr.done(function(){
						$loader.hide();
						$state.show();
					}).fail(function(){
						var $error = this.$element.find('.error');
						$loader.hide();
						$error.show();
						setTimeout(function(){
							$error.hide();
							$state.show();
						}, 1000);
					});
					
					return dfr;
				},
				
				updateState: function(){
					var setState = $.proxy(this.setState, this);
					
					// get the state from the device
					var value = sensor.data('status');
					if(typeof value==='undefined'){
						if(sensor.methods().indexOf('getStatus') !== -1){
							sensor.execute('getStatus').done(setState);
						}
					} else {
						setState(value);
					}
				},
				
				setState: function(state){
					this.state = !!state;
					this.$element.find('svg.state').css('fill',!!state ? '#f4f142' : '#cacaca');
					console.log('!!!!!!!!! setstate');
				},
				
				destroy: function(){
					sensor.off('updated', this.resourceUpdateFn);
					widget.destroy.call(this);
				}
				
			});
		}
		
	};
	
	
}));