(function(){
	
	
	var extract = function(obj,properties){
		var keys = Object.keys(obj), extracted = {};
		for(var i=0; i<keys.length; i++){
			if(properties.indexOf(keys[i])>=0){
				extracted[keys[i]] = $.isPlainObject(obj[keys[i]]) ? jQuery.extend(true, {}, obj[keys[i]]) : obj[keys[i]];
				delete obj[keys[i]];
			}
		}
		return extracted;
	}
	
	
	/**
	 * @description Pop up a save dialog
     * @param {object} opt options
     */
	function SaveDialog(opt){
		
		var deferred = $.Deferred(),
			rejectOnClose = true;
		
		if(typeof opt == 'function')
			opt = {
				done:opt
			};
		
		var options = $.extend({
				filter: null, // function(resource) -> return boolean
				title: "Save",
				done: null, // done(resource) // the selected resource for saving, (must return a deferred object when this operation is asynchronous)
				preset: null, // a resource instance
				size: null, // size of the modal dialog
				canCreate: true, // if the user is able to create a new resource
				createPreset: null // create preset data as { name: "", type: 'File'|'Table'|'App'}
			},opt),
			localOptions = extract(options,['filter','title','done','preset','size','canCreate','createPreset']);
		
		
		var success = function(resource){
			rejectOnClose = false; // the modal may be closed before the done callback is finished
			
			$browser.modal('hide',function(){
				deferred.resolve(resource);
			});
		}
		
		
		var rowEvents = function(){
			var evfct = function(e){
				var resource = e.data.item;
				if(!localOptions.filter || localOptions.filter(resource)){
					e.stopImmediatePropagation(); // disable default behaviour
					success(resource);
				}
			};
			if(EThing.utils.isTouchDevice){
				return {
					'click': evfct
				}
			}
			else
				return {
					'dblclick': evfct
				};
		}
		
		var btns = {
			'+Save': function(){
				
				var $this = $(this),
					browser = $this.browser(),
					selection = browser.selection();
				
				if(selection.length == 0){
					alert('No resource selected !');
					return false;
				}
				
				success(selection[0]);
				
			},
			'!Cancel': null
		};
		
		if(localOptions.canCreate){
			btns['Create a new resource'] = function(){
				
				$('<div>')
					.form({
						'type': {
							input: ['File','Table','App'] // save for Device is meaningless
						},
						'name': {
							input: 'text',
							validator: $.Form.validator.NotEmpty
						}
					})
					.modal({
						title: 'Create a new resource',
						buttons:{
							'+Create': function(){
								
								var $this = $(this);
								
								$this.form().validate().done(function(props){
									EThing[props.type].create({
										name: props.name
									},function(r){
										if(r instanceof EThing.Resource){
											// the creation was successfull, close the dialog and reload the savedialog
											EThing.arbo.add(r);
											$this.modal('hide');// will be autoremoved
										}
										else
											// print the error message but do not close the modal dialog
											$this.form().setError(r.message);
									});
								});
								
								return false;
							},
							'!Cancel': null
						},
						size: localOptions.size
					}).form('setValue',localOptions.createPreset);
				
				return false; // do not close the dialog
			};
		}
		
		var $browser = $('<div>')
			.browser($.extend(true,{
					model:{
						filter : function(r){
							return localOptions.filter && !(r instanceof EThing.Folder) ? localOptions.filter(r) : true;
						}
					},
					selectable:{
						enable: true,
						limit: 1,
						filter: localOptions.filter
					},
					loaded: function(){
						if(localOptions.preset)
							this.select(localOptions.preset);
					}
				},options))
			.modal({
				title: localOptions.title,
				buttons: btns,
				size: localOptions.size
			})
			.on('hidden.bs.modal',function(){
				if(rejectOnClose)
					deferred.reject(null); // the user close the dialog, gives null as the parameter
			});
		
		return deferred.promise();
		
	}
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery) {
		window.jQuery.SaveDialog = SaveDialog;
    }
	
	
})();
