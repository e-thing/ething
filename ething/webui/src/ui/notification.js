(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','ui/core','css!ui/notification','bootstrap'], factory);
    }
}(this, function ($, UI) {
	
	var Notification = {
		
		cnt: 0,
		
		$element: $('<div id="notification">'),
		
		show: function(message, type, duration){
			var self = this;
			
			type = type || 'info';
			duration = duration || 0;
			
			var id = ++this.cnt;
			
			var $noti = $('<div class="alert alert-'+type+'" role="alert" id="notification-'+id+'">').append(
				duration ? null : '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>',
				'<h4>'+type+'</h4>',
				'<p>'+String(message)+'</p>'
			);
			
			this.$element.append($noti, '<div class="clearfix">');
			
			if(duration){
				setTimeout(function(){
					self.hide(id);
				}, duration);
			}
			
			return id;
		},
		
		hide: function(id){
			var $noti = this.$element.find('.alert#notification-'+id);
			var $clearfix = $noti.next();
			$noti.remove();
			$clearfix.remove();
		},
		
		clear: function(){
			this.$element.empty();
		}
		
	};
	
	UI.on('initialized', function(){
		UI.$element.append(Notification.$element);
	})
	
	
	UI.Notification = Notification;
	
	
	return Notification;
}));