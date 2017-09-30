(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    }
}(this, function ($) {
	
	
	return {
		
		require: ['widget/Widget'],
		
		instanciate: function(sensor, options, Widget){
			
			var widget = Widget({
				title: sensor.basename()
			});
			
			return $.extend({}, widget, {
				
				draw: function(){
					
					widget.draw.call(this);
					
					this.$element.empty().append(
				
						$('<div>').append(
							$('<div class="temp">').html([
								$('<span class="value">').html(-10).css({
									'font-size': '52px'
								}),
								$('<span class="unit">').html('&#8451;').css({
									'font-size': '16px'
								})
							]).css({
								'display': 'inline-block'
							}),
							$('<div>').html([
								$('<div class="hum">').html([
									$('<span class="value">').css({
										'font-size': '22px',
										'margin-left': '10px'
									}),
									$('<span class="unit">').html('%').css({
										'font-size': '16px'
									})
								]),
								$('<div class="baro">').html([
									$('<span class="value">').css({
										'font-size': '22px',
										'margin-left': '10px'
									}),
									$('<span class="unit">').css({
										'font-size': '16px'
									})
								])
							]).css({
								'display': 'inline-block',
								'text-align': 'left'
							})
						).css({
							'text-align': 'center'
						})
					).attr('style','display: -webkit-box;display: -moz-box;display: -ms-flexbox;display: -webkit-flex;display: flex;').css({
						'display': 'flex',
						'-webkit-flex-direction': 'column',
						'-moz-flex-direction': 'column',
						'-ms-flex-direction': 'column',
						'-o-flex-direction': 'column',
						'flex-direction': 'column',
						'justify-content': 'center',
						'color': widget.getDefaultColor()
					});
					
					this.onUpdateResource = $.proxy(function(){
						
						var temp = sensor.data('TEMP');
						var hum = sensor.data('HUM');
						var baro = sensor.data('BARO');
						
						this.$element.find('.temp .value').html(Math.round(temp));
						
						if(typeof hum === 'number')
							this.$element.find('.hum .value').html(Math.round(hum));
						this.$element.find('.hum').toggle(typeof hum === 'number');
						
						if(typeof baro === 'number'){
							var baro_unit = 'Pa';
							if(baro > 1000){
								baro /= 1000;
								baro_unit = 'kPa';
							}
							this.$element.find('.baro .value').html(Math.round(baro));
							this.$element.find('.baro .unit').html(baro_unit);
						}
						this.$element.find('.baro').toggle(typeof baro === 'number');
						
						widget.setFooter(sensor.modifiedDate().toLocaleString());
					}, this);
					
					sensor.on('updated', this.onUpdateResource);
					
					this.onUpdateResource();
				},
				
				destroy: function(){
					sensor.off('updated', this.onUpdateResource);
					widget.destroy.call(this);
				}
				
			});
			
		}
		
	};
	
	
}));