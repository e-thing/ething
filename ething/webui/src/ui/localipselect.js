(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','form'], factory);
    } else {
        // Browser globals
        root.LocalIpSelect = factory(root.jQuery,root.Form);
    }
}(this, function ($, Form) {
	
	
	
	var LocalIpSelect = function(options){
		
		Form.Input.call(this, $.extend({
			value: ''
		},options));
		
	}
	Form.inherits(LocalIpSelect,Form.Input);
	
	LocalIpSelect.prototype.createView = function(){
		var $view = $('<div class="f-localipselect">'), self = this;
		
		$view.html(
			'<div class="input-group">'+
			  '<input type="text" class="form-control" placeholder="ip / host">'+
			  '<div class="input-group-btn">'+
				'<button class="btn btn-primary dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><span class="glyphicon glyphicon-search" aria-hidden="true"></span></button>'+
				'<ul class="dropdown-menu dropdown-menu-right">'+
				  '<div class="net-scan">'+
					'<p class="text-center">'+
						'<button type="button" class="btn btn-primary net-scan-scan"><span class="glyphicon glyphicon-search" aria-hidden="true"></span> scan</button>'+
					'</p>'+
					'<p>'+
					  '<div class="list-group">'+
					  '</div>'+
					'</p>'+
				  '</div>'+
				'</ul>'+
			  '</div>'+
			'</div>'+
			'<div class="alert alert-danger" role="alert"></div>'
		);
		
		this.$input = $view.find('input[type="text"]');
		this.$error = $view.find('.alert').hide();
		
		$view.find('button.net-scan-scan').click(function(evt){
			
			evt.stopImmediatePropagation();
			
			var $content = $view.find('.list-group').html('<p class="text-center">scanning...</p>');
			
			$.getJSON('/api/utils/net_list', function(items){
				
				if(items.length===0) {
					$content.html('<p class="text-center">nothing found...</p>');
					return;
				}
				
				$content.empty();
				
				items.forEach(function(item){
					
					var $h = $(
						'<a href="#" class="list-group-item">'+
						  '<h4 class="list-group-item-heading">'+item.ip+'</h4>'+
						  '<p class="list-group-item-text">mac address: '+(item.mac || 'unknown')+'</p>'+
						'</a>'
					);
					
					if(item.vendor)
						$h.append('<p class="list-group-item-text">vendor: '+(item.vendor || 'unknown')+'</p>');
					if(item.hostname)
						$h.append('<p class="list-group-item-text">hostname: '+(item.hostname || 'unknown')+'</p>');
					
					$h.click(function(evt){
						self.value(item.ip);
						evt.preventDefault();
					});
					
					$content.append($h);
					
				});
				
			});
			
		});
		
		if(typeof this.options.placeholder == 'string')
			this.$input.attr('placeholder', this.options.placeholder);
		if(this.options.readonly)
			this.$input.attr('disabled', 'disabled');
		if(this.options.focus)
			this.$input.attr('autofocus', 'autofocus');
		
		var timer = null;
		
		this.$input.change(function(){
			if(timer!==null){
				clearTimeout(timer);
				timer = null;
			}
			self.update();
		});
		
		setTimeout(function(){
			self.$input.keyup(function(){
				if(timer!==null)
					clearTimeout(timer);
				timer = setTimeout(function(){
					self.update();
				}, 250);
			});
		}, 1);

		return $view;
	}
	
	LocalIpSelect.prototype.updateView = function(reason){
		Form.Input.prototype.updateView.call(this);
		
		this.hasError() ? this.$error.html(this.getErrors()[0].message).show() : this.$error.hide();
		this.$view.toggleClass('has-error',this.hasError());
		
		if(!this.hasError() && reason !== 'updateError'){
			this.$input.val(this.value_ || '');
		}
	}
	
	LocalIpSelect.prototype.getViewValue = function(){
		return this.$input.val() || '';
	}
	
	
	Form.LocalIpSelect = LocalIpSelect;
	
	
	return LocalIpSelect;
	
}));