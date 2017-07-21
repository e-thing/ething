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
			title: null,
			item: null,
			value: undefined,
			size: null,
			validLabel: '+Apply',
			cancelLabel: 'Cancel',
			loaded: null
		},opt);
		
		var modalOptions = $.extend(true,{
			buttons: {}
		},extract(options,['title','size']));
		
		
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
		modalOptions.buttons[ extract(options,'cancelLabel') ] = null;
		
		
		var modalDfr = $.Deferred();
		var formDfr = $.Deferred();
		
		modalOptions.shown = function(){
			modalDfr.resolve();
		};
		
		var $form = $('<div>').form(options.item, options.value, function(){
			formDfr.resolve();
		});
		
		var $error = $('<div class="alert alert-danger" role="alert">').hide();
		var $modal = $('<div>').append($form,$error).modal(modalOptions);
		
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
