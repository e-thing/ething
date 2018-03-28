(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','ething','ui/browser','ui/modal'], factory);
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
	 * @description Pop up an open dialog
     * @param {object} opt options
     */
	function OpenDialog(opt){
	
		var deferred = $.Deferred(),
			rejectOnClose = true;
		
		if(typeof opt == 'function')
			opt = {
				done:opt
			};
		
		var options = $.extend({
				filter: null, // function(resource) -> return boolean
				limit: 1, // limit the selection to a specific number
				title: "Open",
				preset: null, // a resource instance
				size: null // size of the modal dialog
			},opt),
			localOptions = extract(options,['filter','limit','title','preset','size']);
		
		
		var success = function(resource){
			rejectOnClose = false; // the modal may be closed before the done callback is finished
			
			$browser.modal('hide',function(){
				deferred.resolve(resource);
			});
		}
		
		// table explorer
		
		var rowEvents = function(){
			var evfct = function(e){
				var resource = e.data.item;
				if(!localOptions.filter || localOptions.filter(resource)){
					e.stopImmediatePropagation(); // disable default behaviour
					success([resource]);
				}
			};
			if(isTouchDevice){
				if(localOptions.limit==1)
					return {
						'click': evfct
					}
			}
			else
				return {
					'dblclick': evfct
				};
			return {};
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
						limit: localOptions.limit,
						filter: localOptions.filter
					},
					loaded: function(){
						if(localOptions.preset)
							this.select(localOptions.preset);
					},
					row: {
						events: rowEvents()
					}
				},options))
			.modal({
				title: localOptions.title,
				buttons: {
					'+Open': function(){
						
						var $this = $(this),
							selection = $this.browser().selection();
						
						if(selection.length == 0){
							alert('No resource selected !');
							return false;
						}
						
						success(selection);
					},
					'!Cancel': null
				},
				size: localOptions.size
			})
			.on('hidden.bs.modal',function(){
				if(rejectOnClose)
					deferred.reject(null); // the user close the dialog, gives null as the parameter
			});
		
		
		return deferred.promise();
		
	}
	
	
	/* register as a plugin in jQuery */
	$.OpenDialog = OpenDialog;
	
	
}));
