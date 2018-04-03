(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ui/core', 'css!ui/container'], factory);
    }
}(this, function ($, UI) {
	
	console.log('loading ui/container.js');
	
	
	var Container = {
		$element : $('<div>'),
		
		set: function(element, id){
			
			var $element = $(element);
			
			$('body').attr('id', UI.path().replace('/','-'));
			$('body').attr('data-page', UI.path());
			
			$element.addClass('ui-container');
			
			this.$element.replaceWith($element);
			this.$element = $element;
			
			return $element;
		}
	};
	
	UI.Container = Container;
	
	
	UI.on('initialized', function(){
		UI.$element.append(Container.$element);
	});
	
	UI.on('ui-pageChange', function(){
		$('body').removeAttr('id');
		var $loader = $('<div id="loader">loading...</div>');
		Container.$element.replaceWith($loader);
		Container.$element = $loader;
	});
	
	return Container;
	
}));