(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','js/ui','bootstrap', 'css!./modal'], factory);
    }
}(this, function ($, UI) {

	
	if(!$.fn.modal){
		console.error('bootstrap.js not loaded ! Needed for the modal plugin.');
		return;
	}
	
	var BsModal = $.fn.modal.Constructor;
	
	
	
	/*
	 * Enable Overlapping modals
	 * see : https://github.com/twbs/bootstrap/issues/15260
	*/
	(function(Modal) {
	  
	  var show = Modal.prototype.show;
	  
	  Modal.prototype.show = function() {
		this.modalOpen = !this.$body.hasClass('modal-open');
		
		// hide the previous modal
		this.$body.children('.modal:visible').last().hide();
		this.$body.children('.modal-backdrop:visible').last().hide();
		
		show.apply(this, arguments);
	  };
	  
	  Modal.prototype.hideModal = function () {
		var that = this
		this.$element.hide()
		this.backdrop(function () {
		  if (that.modalOpen) that.$body.removeClass('modal-open')
		  // restore the previous modal
		  that.$element.prevAll('.modal:hidden').last().show();
		  that.$element.prevAll('.modal-backdrop:hidden').last().show();
		  that.resetAdjustments()
		  that.resetScrollbar()
		  
		  if(typeof this.epilogFct === 'function'){
			  this.epilogFct.call(that);
		  }
		  
		  that.$element.trigger('hidden.bs.modal')
		})
	  }
	  
	})(BsModal);
	
	
	var Modal = function (element, options) {
		
		var $element = $(element),
			self = this,
			id = 'modal-'+String(Math.round(Math.random()*10000)),
			hasParent = $element.parent().length > 0;
		
		this.options = $.extend(true,{
			title: '&nbsp;',
			buttons: {},
			removeOnClose: !hasParent, // destroy element on close
			size: null,
			shown: null, // executed once this modal dialog is shown
			closeButton: true
		},BsModal.DEFAULTS, {
			backdrop: 'static'
		}, $element.data(), options);
		
		
		if(!$element.is('.modal')){
			
			// the element represent the body of the modal dialog
			var $wrapper = $(
				'<div class="modal fade">'+
					  '<div class="modal-dialog'+(this.options.size ? ' modal-'+this.options.size : '')+'">'+
						'<div class="modal-content">'+
							'<div class="modal-header">'+
								(this.options.closeButton ? '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>' : '')+
								'<h4 class="modal-title"></h4>'+
							'</div>'+
							'<div class="modal-body"></div>'+
						'</div>'+
					  '</div>'+
					'</div>'
				);
			
			$wrapper.find('.modal-body').append($element);
			
			(function($p,$e){
				$p.on('show.bs.modal shown.bs.modal hide.bs.modal hidden.bs.modal loaded.bs.modal',function(e){
					$e.triggerHandler(e);
				});
			})($wrapper,$element);
			
			$element = $wrapper;
			
		}
		
		if(this.options.title){
			$element.find('.modal-title').html(this.options.title);
		}
		
		if(this.options.buttons){
			
			var $btns = []; 
			
			var createCallback = function(cb){ // if the callback return false, the modal dialog is not closed. it it returns a function, that function will be fired at the very end of the closing (after any animation or hash event)
				return function(e){
					var r = (typeof cb == 'function') ? cb.call(element) : true;
					if(r!==false){
						self.hide(r);
					}
				};
			}
			
			for(var btnName in this.options.buttons){
				var buttonOptions = this.options.buttons[btnName], $btn;
				
				if(typeof buttonOptions == 'function')
					buttonOptions = {
						handler: buttonOptions
					};
				
				if($.isPlainObject(buttonOptions) || buttonOptions===null){
					
					buttonOptions = $.extend({
						'handler': null,
						'class': null,
						'icon': null
					},buttonOptions);
					
					buttonOptions['class'] = buttonOptions['class'] || '';
					
					if(/^\+/.test(btnName)){
						buttonOptions['class'] += " btn-primary";
						btnName = btnName.substr(1);
						if(!buttonOptions['icon']) buttonOptions['icon'] = 'glyphicon-ok';
					}
					else if(/^\!/.test(btnName)){
						buttonOptions['class'] += " btn-warning";
						btnName = btnName.substr(1);
						if(!buttonOptions['icon']) buttonOptions['icon'] = 'glyphicon-remove';
					}
					else
						buttonOptions['class'] += " btn-default";
					
					var icon = '';
					if(buttonOptions['icon']){
						if(/^glyphicon-/.test(buttonOptions['icon']))
							icon = '<span class="glyphicon '+buttonOptions['icon']+'" aria-hidden="true"></span>';
						else
							icon = buttonOptions['icon'];
						icon += ' ';
					}
					$btn = $('<button type="button" class="btn '+buttonOptions['class']+'">'+icon+btnName+'</button>')
								.click(createCallback(buttonOptions.handler));
				}
				else
					$btn = buttonOptions;
				
				$btn.addClass('modal-btn');
				$btn.attr('data-name', btnName);
				
				$btns.push($btn);
			}
			
			if($btns.length){
				var $footer = $element.find('.modal-footer');
				if(!$footer.length){
					$footer = $('<div class="modal-footer">').appendTo($element.find('.modal-content'));
				}
				$footer.addClass('btn-toolbar form-inline').append($btns);
			}
		}
		
		
		
		$element.attr('data-id',id);
		
		BsModal.call(this, $element[0], this.options);
		
		// events
		this.epilogFct = null;
		var epilog = function(){
			// this function is executed at the very end :
			//  - after any animation
			//  - after any hash change
			
			if(typeof self.epilogFct == 'function'){
				self.epilogFct.call(element);
				self.epilogFct = null;
			}
		}
		
		$element.on('hidden.bs.modal', function (e) {
			if(self.options.removeOnClose)
				self.options.removeOnClose==='detach' ? $element.detach() : $element.remove();
			
			epilog();
		});
		
		var onFirstShown = this.options.shown || null;
		$element.on('shown.bs.modal', function (e) {
			if(onFirstShown)
				onFirstShown.call(self)
			
			epilog();
		});
		
		if(typeof this.options.customize === 'function')
			this.options.customize.call(this, $element);
		
		if(this.options.show)
			this.show();
		
	}
	Modal.prototype = Object.create(BsModal.prototype);
	
	Modal.prototype.hide = function(callback){
		if(typeof callback == 'function')
			this.epilogFct = callback;
		BsModal.prototype.hide.call(this);
	}
	
	// disable the buttons
	Modal.prototype.disable = function(){
		this.$element.find('.modal-footer .modal-btn').attr('disabled','disabled');
	}
	Modal.prototype.enable = function(){
		this.$element.find('.modal-footer .modal-btn').removeAttr('disabled');
	}
	
	Modal.prototype.buttons = function(){
		return this.$element.find('.modal-footer .modal-btn');
	}
	
	
	
	/* register as a plugin in jQuery */
	
	$.fn.modal = function(){
		var args = [].slice.call(arguments);
		
		if (this[0]) { // this[0] is the renderTo div
			
			var instance = $(this[0]).data('modal');
			
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
			instance = new Modal(this[0],args[0],args[1],args[2],args[3],args[4],args[5],args[6]);
			$(this[0]).data('modal',instance);
			
			return this;
		}
	};
	
	UI.Modal = Modal;
	
	UI.on('ui-pageChange', function(){
		// remove all modal dialogs of the current view
		$('body>.modal, body>.modal-backdrop').remove();
		$('body').removeClass('modal-open');
	});
	
	return Modal;
	
}));
