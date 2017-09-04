(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    }
}(this, function ($) {
	
	
	
	function Widget(opt){
		
		var self = {};
		
		// create the dom
		var $element = $('<div>').addClass('db-widget');
		
		
		
		var setError = function(err){
			if(err===false){
				$element.siblings('.db-widget-err').hide();
				return this;
			}
			console.error(err);
			$element
				.siblings('.db-widget-err')
				.html('<p><span class="glyphicon glyphicon-warning-sign" aria-hidden="true"></span><br>'+((typeof err == 'object' && err !== null && typeof err.message == 'string') ? err.message : (err || 'error'))+'</p>')
				.show();
			return this;
		};
		
		
		return $.extend(self, {
			
			
			$element : $element,
			
			setError: setError,
			
			draw: function(){
				// to be implemented
				
				if(opt.title) this.$element.attr('data-title',opt.title);
				if(opt.footer) this.$element.attr('data-footer',opt.footer);
				
				return self;
			},
			
			destroy: function(){
				// to be implemented
				return self;
			},
			
			resize: function(){
				// to be implemented
				return self;
			},
			
			setTitle: function(f){
				if(f) this.$element.attr('data-title',f);
				else this.$element.removeAttr('data-title');
			},
			
			setFooter: function(f){
				if(f) this.$element.attr('data-footer',f);
				else this.$element.removeAttr('data-footer');
			}
			
		});
		
	}
	
	return Widget;
	
}));