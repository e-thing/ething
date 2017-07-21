(function(){
	
	
	/*
	* inspired from http://circle.firchow.net
	*/
	
	var CircleBar = function (element, options){
		
		this.$element = $(element);
		
		this.$element.html(
			'<span></span>'+
			'<div class="slice">'+
				'<div class="bar"></div>'+
				'<div class="fill"></div>'+
			'</div>'
		).addClass('c100');
		
		this.min = typeof options.min === 'undefined' ? 0 : options.min;
		this.max = typeof options.max === 'undefined' ? 100 : options.max;
		this.unit = typeof options.unit === 'undefined' ? '%' : options.unit;
		
		// color
		this.$element.find('.bar, .fill').css('border-color',options.color || '#307bbb');
		this.$element.children('span').css('color',options.color || '#307bbb');
		
		this.val(options.value || 0);
	}
	
	CircleBar.prototype.val = function(value){
		if(typeof value === 'undefined'){
			return this.value;
		} else {
			this.value = parseInt(value);
			if(isNaN(this.value)) this.value = 0;
			this.redraw();
		}
	}
	
	CircleBar.prototype.redraw = function(){
		var label = this.value+this.unit;
		this.$element.children('span').text(label);
		
		var normValue = (this.value - this.min) / (this.max - this.min);
		var angle = Math.round(360 * normValue);
		this.$element.find('.bar').css({
			transform: 'rotate('+angle+'deg)'
		});
		
		this.$element.toggleClass('p51', angle>180);
		
	}
	
	
	$.fn.circleBar = function(){
		var args = [].slice.call(arguments);
		
		if (this[0]) { // this[0] is the renderTo div
			
			var instance = $(this[0]).data('circleBar');
			
			if(instance){
				if(args.length){
					if(typeof args[0] == 'string'){
						// access the attribute or method
						var prop = instance[args.shift()];
						if(typeof prop == 'function'){
							var r = prop.apply(instance,args);
							return (r === instance) ? this : r; // make it chainable
						}
						else {
							if(args.length==0){
								// getter
								return prop;
							}
							else if(args.length==1){
								// setter
								prop = args[0];
								return this;
							}
						}
					}
				}
				else
					return instance;// When called without parameters return the instance
			}
			
			// if we are are, it means that there is no instance or that the user wants to create a new one !
			// /!\ NOTE : be sure to not emit any event in the constructor, or delay them using the setTimeout function !
			instance = new CircleBar(this[0],args[0],args[1],args[2],args[3],args[4],args[5],args[6]);
			$(this[0]).data('circleBar',instance);
			
			return this;
		}
	};
	
	
})()