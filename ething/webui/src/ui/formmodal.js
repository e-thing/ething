(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','form','ui/modal'], factory);
    } else {
        // Browser globals
        factory(root.jQuery);
    }
}(this, function ($) {
	
	
	function extract(src,fields){
		var o = {}, isarray = true;
		if(!Array.isArray(fields)){
			isarray = false;
			fields = [fields];
		}
		for(var i=0; i<fields.length; i++){
			o[fields[i]] = src[fields[i]];
			delete src[fields[i]];
		}
		return isarray ? o : o[fields[0]];
	}
	
	
	function FormModal(opt,doneCallback){
		
		var options = $.extend(true,{
			header: null,
			title: null,
			item: null,
			value: undefined,
			size: null,
			validLabel: '+Apply',
			cancelLabel: 'Cancel',
			cancellable: true,
			loaded: null,
			customize: null
		},opt);
		
		var modalOptions = $.extend(true,{
			buttons: {}
		},extract(options,['title','size','customize']));
		
		
		// add buttons
		modalOptions.buttons[ extract(options,'validLabel') ] = function(){
			var $this = $(this);
			
			if(typeof doneCallback == 'function'){
				
				$this.modal('disable');
				
				$form.form('submit', function(value){
				
					var r = doneCallback.call(this,value);
					if(typeof r == 'undefined'){
						$this.modal('hide');
						return;
					}
					else if(r !== false){
						$.when(r)
							.done(function(v){
								// close the modal dialog only on success
								$this.modal('hide', v);
							})
							.fail(function(e){
								$this.modal('enable');
								$error.text(typeof e.message == 'string' ? e.message : e).show();
								$form.one('changed.form', function(){
									$error.hide();
								});
							});
					}
					else {
						$this.modal('enable');
					}
				});
				
				return false; // do not close the modal dialog
			}
			
		};
		if(options.cancellable) {
			modalOptions.buttons[ extract(options,'cancelLabel') ] = null;
		} else {
			modalOptions.closeButton = false;
		}
		
		var modalDfr = $.Deferred();
		var formDfr = $.Deferred();
		
		// add show/hide advanced settings
		var userCustomize = modalOptions.customize;
		var $advbtn = $('<button type="button" class="btn btn-link pull-right" data-name="btn-adv-setting">Advanced settings</button>');
		modalOptions.customize = function($modal){
			$advbtn.click(function(){
				$advbtn.text( $modal.find('.modal-dialog').toggleClass('form-expert').hasClass('form-expert') ? 'Hide advanced settings' : 'Advanced settings' );
			}).hide();
			$modal.find('.modal-footer').prepend($advbtn);
			
			if(typeof userCustomize == 'function') userCustomize.apply(this, arguments);
		}
		var updateAdvBtnVisibility = function(){
			if(f) $advbtn.toggle(!!f.$view.find('*:visible > .item-expert').length);
		};
		var f = null;
		formDfr.done(function(form){
			f = form;
			updateAdvBtnVisibility();
			form.change(function(){
				setTimeout(updateAdvBtnVisibility, 1);
			});
		});
		modalDfr.done(function(){
			updateAdvBtnVisibility();
		});
		
		modalOptions.shown = function(){
			modalDfr.resolve();
		};
		
		var $form = $('<div>').form(options.item, options.value, function(){
			formDfr.resolve(this);
		});
		var $header = typeof options.header === 'string' ? $('<p class="m-header">').html(options.header) : null;
		var $error = $('<div class="alert alert-danger" role="alert">').hide();
		var $modal = $('<div>').append($header,$form,$error).modal(modalOptions);
		
		var $validBtn = $modal.modal('buttons').first();
		
		
		$form.on('changed.form', function(){
			$validBtn.prop('disabled', $form.form('hasError'));
		});
		
		$.when(modalDfr, formDfr).done(function(){
			if(typeof options.loaded === 'function')
				options.loaded($form, $modal);
		});
		
		return $modal;
		
	}

	
	/* register as a plugin in jQuery */
	$.FormModal = FormModal;
	



}));
