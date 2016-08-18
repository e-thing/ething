(function(){
	
	
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
			size: null,
			validLabel: '+Apply',
			cancelLabel: 'Cancel'
		},opt);
		
		var modalOptions = $.extend(true,{
			buttons: {}
		},extract(options,['title','size']));
		
		
		// add buttons
		modalOptions.buttons[ extract(options,'validLabel') ] = function(){
			var $this = $(this);
			
			$this.modal('disable').form('validate')
				.done(function(props){
					if(typeof doneCallback == 'function'){
						var r = doneCallback.call(this,props);
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
									$this.form().setError(typeof e.message == 'string' ? e.message : e);
								});
							return;
						}
					}
					$this.modal('enable');
				})
				.fail(function(){
					$this.modal('enable');
				});
			
			return false; // do not close the modal dialog
		};
		modalOptions.buttons[ extract(options,'cancelLabel') ] = null;
		
		
		return $('<div>')
			.form(options)
			.modal(modalOptions)
		
	}

	
	/* register as a plugin in jQuery */
	if (window.jQuery) {
		window.jQuery.FormModal = FormModal;
    }
	



})();
