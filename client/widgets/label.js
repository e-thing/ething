(function(){
	
	
	var Label = function(element,options){
		
		options = $.extend(true,{
			value: {
				tableId: null,
				field: null
			},
			unit: null
		}, options);
		
		var css = {
			'position': 'relative',
			'font-size': '48px',
			'text-align': 'center',
			'color': '#6B6B6B',
			'height': '100%'
		};
		
		var $element = $(element);
		
		$element.css(css);
		
		var $inner = $('<div>').appendTo($element).css({
			'position': 'absolute',
			'top': '0',
			'bottom': '0',
			'left': '0',
			'right': '0',
			'height': '68px',
			'margin': 'auto',
			'white-space': 'nowrap',
			'text-overflow': 'ellipsis',
			'overflow': 'hidden'
		});
		
		EThing.Table.select(options.value.tableId, {
			fields: [options.value.field],
			start: -1,
			length: 1
		}).done(function(data){
			if(data.length && data[0].hasOwnProperty(options.value.field)){
				var $unit;
				if(options.unit)
					$unit= $('<span>').html(options.unit).css({
						'color': '#9C9C9C',
						'font-size': '32px'
					});
			
				$inner.empty().append(
					data[0][options.value.field],
					$unit
				);
			}
		});
		
	}
	
	
	return {
		// must return a function which returns an options object
		factory: function(container, preset){
			var form = new $.Form(container,{
				'value': new $.Form.TableFieldSelect(),
				'unit': 'text'
			});
			
			if(preset)
				form.setValue(preset);
			
			return function(){
				return form.validate();
			}
		},
		
		instanciate: function(element, options){
			new Label(element,options);
		}
	};
	
})()