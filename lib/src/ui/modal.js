(function(){
	
	if(!window.jQuery.fn.modal){
		console.error('bootstrap.js not loaded ! Needed for the modal plugin.');
		return;
	}
	
	var $ = window.jQuery,
		BsModal = $.fn.modal.Constructor;
	
	
	
	/*
	 * Enable Overlapping modals
	 * see : https://github.com/twbs/bootstrap/issues/15260
	*/
	(function(Modal) {
	  var show = Modal.prototype.show;

	  Modal.prototype.show = function() {
		this.modalOpen = !this.$body.hasClass('modal-open');
		show.apply(this, arguments);
	  };

	  Modal.prototype.hideModal = function() {
		var that = this;
		this.$element.hide();
		this.backdrop(function() {
		  if (that.modalOpen) {
			that.$body.removeClass('modal-open');
		  }
		  that.resetScrollbar();
		  that.$element.trigger('hidden.bs.modal');
		});
	  };
	})(BsModal);
	
	
	var Modal = function (element, options) {
		
		var $element = $(element),
			self = this,
			id = 'modal-'+String(Math.round(Math.random()*10000)),
			hiddenModals = null,
			hasParent = $element.parent().length > 0;
		
		this.options = $.extend(true,{
			title: null,
			buttons: {},
			removeOnClose: !hasParent, // destroy element on close
			size: null
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
								'<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+
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
						'class': null
					},buttonOptions);
					
					var extraClass = '';
					if(/^\+/.test(btnName)){
						extraClass += " btn-primary";
						btnName = btnName.substr(1);
					}
					else if(/^\!/.test(btnName)){
						extraClass += " btn-warning";
						btnName = btnName.substr(1);
					}
					else
						extraClass += " btn-default";
					
					$btn = $('<button type="button" class="btn '+buttonOptions['class']+extraClass+'">'+btnName+'</button>')
								.click(createCallback(buttonOptions.handler));
				}
				else
					$btn = buttonOptions;
				
				$btn.addClass('modal-btn');
				
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
		var isHidden = false;
		this.epilogFct = null;
		var epilog = function(){
			// this function is executed at the very end :
			//  - after any animation
			//  - after any hash change
			
			// restore the hidden modals
			
			if(hiddenModals)
				hiddenModals.show();
			
			if(typeof self.epilogFct == 'function'){
				self.epilogFct.call(element);
				self.epilogFct = null;
			}
		}
		
		var hashHandler = function(){
			// remove this modal
			if(window.location.hash.indexOf(id)==-1){ // the hash tag from this modal just disappear, hide it !
				$(window).off('hashchange', hashHandler);
				if(!isHidden){
					self.hide();
				}
				else{
					epilog();
				}
			}
		};
		
		$element.on('hidden.bs.modal', function (e) {
			isHidden = true;
			
			if(self.options.removeOnClose)
				$element.remove();
			
			if(window.location.hash.indexOf(id)>=0){
				history.back();
			}
			else{
				epilog();
			}
			
		});
		
		$element.on('shown.bs.modal', function(){
			window.location.hash += '#' + id;
			$(window).on('hashchange', hashHandler);
		});
		
		$element.on('show.bs.modal', function(){
			// if there is other modal dialog opened, just hide them
			hiddenModals = $('div.modal:visible').not('[data-id="'+self.id+'"]').hide();
		});
		
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
	
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery)
		window.jQuery.addPlugin('Modal',Modal);
	
})();
