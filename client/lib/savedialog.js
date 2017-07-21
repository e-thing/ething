(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','ething','browser','ui/modal'], factory);
    } else {
        // Browser globals
        factory(root.jQuery, root.EThing);
    }
}(this, function ($, EThing) {
	
	var isTouchDevice = navigator ? (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase())) : false;
	
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
				createPreset: undefined // create preset data as { name: "", type: 'File'|'Table'|'App'}
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
			if(isTouchDevice){
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
				
				$.FormModal({
					item: new $.Form.FormLayout({
						items: [{
							name: 'type',
							item: new $.Form.Select(['File','Table','App']) // save for Device is meaningless
						},{
							name: 'name',
							item: new $.Form.Text({
								validators:[$.Form.validator.NotEmpty]
							})
						}],
						value: localOptions.createPreset
					}),
					title: '<span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Create a new resource',
					validLabel: '+Create',
					size: localOptions.size
				},function(props){
					return EThing[props.type].create({
						name: props.name
					});
				});
				
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
	$.SaveDialog = SaveDialog;
	
	
}));
