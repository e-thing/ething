(function (factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','css!./breadcrumb'], factory);
    } else {
        // Browser globals
        factory(jQuery);
    }
}(function ($) {
  'use strict';
  
  var Breadcrumb = function (element, options) {
  
    this.options  = options;
    this.$element = $(element);
	
  };
  
  Breadcrumb.DEFAULTS = {
	onClick: null,
	maxItems: 0 // not including home button which is always displayed, may be a function
  };
  
  
  Breadcrumb.prototype.create = function () {
	
	this.$element.addClass('btn-breadcrumb');
	
	// home button
	this.createItem('<i class="glyphicon glyphicon-home"></i>','');
	
	
  }
  
  
  
  
	Breadcrumb.prototype.createItem = function(name, data){
		var onclick = this.options.onClick;
		return $(
			'<a class="btn btn-default"><div>'+name+'</div></a>'
		).data('d',data).click(function(){
			if($.isFunction(onclick))
				onclick($(this).data('d'));
		}).appendTo(this.$element);
	}
	
	Breadcrumb.prototype.value = function(path){
		
		var parts = (path||'').split('/'),
			p = '', skip = 0,
			maxItems = $.isFunction(this.options.maxItems) ? this.options.maxItems() : this.options.maxItems;
		
		// clean first
		this.$element.children().each(function(index, el) {
			if(index>0)
				$(el).remove();
		});

		if(maxItems && parts.length > maxItems){
			// some items must be removed
			skip = parts.length - maxItems + 1; // add 1 for the '...' items
			this.createItem('...',null);
		}
		
		for(var i=0; i<parts.length; i++)
			if(parts[i].length>0){
				if(p.length) p+='/';
				p += parts[i];
				if(i>=skip)
					this.createItem(parts[i],(i+1<parts.length) ? p : null);
			}
		
	}
	
	Breadcrumb.prototype.destroy = function () {
		this.$element
			.removeClass("btn-breadcrumb")
			.empty();
	}
	
	
  // PLUGIN DEFINITION
  // =======================

  function Plugin(option, v) {
	
	var $this   = $(this);
	var data    = $this.data('breadcrumb');
	if(!data){
		var options = $.extend({}, Breadcrumb.DEFAULTS, $this.data(), typeof option == 'object' && option);
		$this.data('breadcrumb', (data = new Breadcrumb(this, options)));
		data.create();
	}
	
	
	if(option==="value" && typeof v == 'undefined')
		return data[option]();
	
    return this.each(function () {
      if (typeof option == 'string') data[option](v);
      else if (typeof option == 'object' && option.hasOwnProperty('value')) data.value(option.value);
    })
  }

  var old = $.fn.breadcrumb;

  $.fn.breadcrumb             = Plugin;
  $.fn.breadcrumb.Constructor = Breadcrumb;


  // TIMESPAN NO CONFLICT
  // =================

  $.fn.breadcrumb.noConflict = function () {
    $.fn.breadcrumb = old
    return this
  }
	
}));
