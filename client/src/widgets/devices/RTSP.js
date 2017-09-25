(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    }
}(this, function ($) {
	
	
	return {
		
		factory: function(container, preset){
			
			var form = new $.Form(container,new $.Form.FormLayout({
				items:[{
					name: 'refreshPeriod',
					label: 'refresh period',
					item: new $.Form.Number({
						validators: [$.Form.validator.Integer],
						value: 60,
						minimum: 1,
						suffix: 'secondes'
					}),
					checkable: true
				}]
			}), preset);
			
			return function(){
				return form.submit();
			}
		},
		
		require: ['widget/Widget','imageviewer'],
		
		instanciate: function(device, options, Widget){
			
			
			var imageViewerOptions = {
				header: {
					enable: true,
					showOnHover: true
				},
				elements: [{
					name: '<span class="glyphicon glyphicon-facetime-video" aria-hidden="true"></span> '+device.basename(),
					content: function(){
						return device.execute('snapshot', null, true);
					}
				}]
			};
			
			
			var $iv, timerId = null;
			
			var widget = $.extend(Widget(), {
				
				draw: function(){
					
					$iv = $('<div>').css({
						'height': '100%',
						'background-color': '#ffffff',
						'color': '#4e4e4e'
					}).imageViewer(imageViewerOptions).appendTo(this.$element);
					
					if(options.refreshPeriod)
						timerId = setInterval(function(){
							$iv.imageViewer('refresh');
						}, (options.refreshPeriod) * 1000);
				},
				
				destroy: function(){
					$iv.imageViewer('destroy');
					if(timerId!==null) clearInterval(timerId);
				}
				
			});
			
			return widget;
			
		}
		
	};
	
	
}));