(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'ui/utils', 'form'], factory);
    }
}(this, function ($, EThing, UI) {
	
	return {
		
		'bases': ['Resource'],
		
		'icon': '<g transform="scale(0.035) translate(200,200)" stroke-width="0"><rect y="22.261" width="512" height="100.174"/><rect y="155.826" width="144.696" height="89.043"/><rect y="400.696" width="144.696" height="89.043"/><rect y="278.261" width="144.696" height="89.043"/><rect x="178.087" y="155.826" width="155.826" height="89.043"/><rect x="178.087" y="400.696" width="155.826" height="89.043"/><rect x="178.087" y="278.261" width="155.826" height="89.043"/><rect x="367.304" y="155.826" width="144.696" height="89.043"/><rect x="367.304" y="400.696" width="144.696" height="89.043"/><rect x="367.304" y="278.261" width="144.696" height="89.043"/></g>',
		
		'properties' : {
			"length": {
				label: "rows",
				default: 0
			},
			"contentModifiedDate": {
				label: "content last update",
				formatter: UI.dateToString
			},
			"maxLength": {
				label: "max rows",
				formatter: function(v){
					return v ? String(v) : "none";
				},
				isOptional: true,
				editable:function(){
					return new $.Form.Number({
						minimum: 1,
						value: 100
					});
				}
			},
			"expireAfter": {
				label: "expire after",
				description: "This resource will be automatically removed after a specific duration of inactivity.",
				formatter: function(v){
					return v ? UI.dateDiffToString(v) : "never";
				},
				isOptional: true,
				editable: function(){
					return new $.Form.Duration({
						minute: false,
						hour: true,
						day: true,
						value: 86400
					});
				}
			}
		}
	}
}))