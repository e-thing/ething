(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form', 'ui/resourceselect'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		
		'bases': ['Device'],
		
		'icon': '<g transform="scale(0.05) translate(160,160)" stroke-width="0"><path d="M266.911,109.898c-20.498,0-37.894,13.125-44.354,31.408H116.406l51.734-51.732c6.147,2.936,13,4.631,20.27,4.631c26.004,0,47.104-21.095,47.104-47.104C235.513,21.087,214.414,0,188.41,0c-26.005,0-47.104,21.087-47.104,47.102c0,7.268,1.695,14.122,4.631,20.264l-61.278,61.288c-8.59-11.383-22.201-18.747-37.558-18.747C21.093,109.906,0,130.991,0,157.007c0,26.004,21.093,47.103,47.101,47.103c15.365,0,28.968-7.361,37.558-18.755l61.278,61.286c-2.936,6.151-4.631,13.004-4.631,20.27c0,26.004,21.099,47.104,47.104,47.104c26.004,0,47.104-21.1,47.104-47.104c0-26.017-21.1-47.1-47.104-47.1c-7.27,0-14.122,1.691-20.27,4.629l-51.734-51.732h106.151c6.468,18.286,23.855,31.402,44.354,31.402c26.009,0,47.104-21.099,47.104-47.103C314.014,130.991,292.919,109.898,266.911,109.898z M188.41,31.402c8.664,0,15.701,7.025,15.701,15.699c0,8.668-7.037,15.701-15.701,15.701s-15.701-7.033-15.701-15.701C172.708,38.428,179.746,31.402,188.41,31.402z M47.102,172.708c-8.666,0-15.699-7.037-15.699-15.701c0-8.674,7.033-15.701,15.699-15.701c8.668,0,15.701,7.027,15.701,15.701C62.803,165.671,55.77,172.708,47.102,172.708z M188.41,251.214c8.664,0,15.701,7.021,15.701,15.697c0,8.664-7.037,15.701-15.701,15.701s-15.701-7.037-15.701-15.701C172.708,258.234,179.746,251.214,188.41,251.214zM266.911,172.708c-8.66,0-15.697-7.037-15.697-15.701c0-8.674,7.037-15.701,15.697-15.701c8.664,0,15.701,7.027,15.701,15.701C282.612,165.671,275.575,172.708,266.911,172.708z"/></g>',
		
		'description' : 'See <a href="//www.mysensors.org" target="_blank">MySensors website</a>',
		
		'name': 'MySensors Node',
		
		'path' : ['MySensors', 'Node'],
		
		'properties' : {
			"gateway": {
				editable: function(){
					return new $.Form.ResourceSelect({
						filter: function(r){
							return r.isTypeof("MySensorsGateway");
						},
						validators: [$.Form.validator.NotEmpty]
					});
				}
			},
			"nodeId": {
				editable: function(){
					return new $.Form.Number({
						minimum: 1,
						maximum: 254,
						value: 1,
						placeholder: 'nodeId',
						validators: [$.Form.validator.Integer]
					});
				}
			},
			"sketchName": {
				
			},
			"sketchVersion": {
				
			},
			"smartSleep": {
				editable: function(){
					return new $.Form.Checkbox();
				}
			}
		}
	}
}))