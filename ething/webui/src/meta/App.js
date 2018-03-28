(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['require', 'jquery', 'ething', 'ui/utils', 'form'], factory);
    }
}(this, function (require, $, EThing, UI) {
	
	return {
		
		'bases': ['Resource'],
		
		'icon': '<text x="16" y="24" font-size="22" font-weight="bold" font-family="Arial" text-anchor="middle">A</text>',
		
		'properties' : {
			"mime": {
				label: "mime type"
			},
			"length": {
				label: "rows",
				default: 0
			},
			"size": {
				formatter: UI.sizeToString,
				default: 0
			},
			"icon": {
				isOptional: true,
				get: function(r){
					return r.iconLink(true);
				},
				editable: function(r){
					return new $.Form.Image({
						imageTransform: function(blob){
							// crop the image into a 128x128px image
							return imageSquareResizeBlob(blob, 128);
						}
					});
				}
			},
			"scope": {
				label: 'permission',
				description: 'Restrict this resource to the following permissions :',
				formatter: function(){
					return null;
				},
				editable:function(resource){
					
					// async
					var depDfr = $.Deferred();
					require(["scopeform"], function(){
						depDfr.resolve(new $.Form.CustomInput({
							input: function(){
								var $input = $('<div>').text('loading...'), self = this;
								$input.empty().scopeForm();
								$input.on('change', function(){
									self.update();
								});
								return $input;
							},
							set: function($e,v){
								$e.scopeForm('value',v)
							},
							get: function($e){
								return $e.scopeForm('value');
							},
							value: ''
						}));
						
					});
					
					return depDfr;
				}
			},
			"version": {
				formatter: function(v){
					return v || 'unversioned';
				}
			}
		}
	}
}))