(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'ui/utils', 'form'], factory);
    }
}(this, function ($, EThing, UI) {
	
	return {
		
		'bases': ['Resource'],
		
		'icon': '<text x="16" y="24" font-size="22" font-weight="bold" font-family="Arial" text-anchor="middle">D</text>',
		
		'creatable': false,
		
		'properties' : {
			"lastSeenDate": {
				label: "last seen",
				formatter: function(date){
					return date ? UI.dateToString(date) : 'never';
				}
			},
			"battery": {
				formatter: function(batValue){
					return (typeof batValue == 'number') ? batValue+"%" : 'no battery';
				}
			},
			"connected": {
				formatter: function(v){
					return v ? 'connected' : 'disconnected';
				}
			},
			"location": {
				formatter: function(v){
					var parts = [];
					if(v){
						if( typeof v.latitude != 'undefined' && typeof v.longitude != 'undefined')
							parts.push( v.latitude+"N "+v.longitude+"E" );
						if( typeof v.place != 'undefined' ) parts.push(v.place);
						if( typeof v.floor != 'undefined' ) parts.push('floor:'+v.floor);
						if( typeof v.room != 'undefined' ) parts.push(v.room);
					}
					return parts.length ? parts.join(',') : 'somewhere on earth';
				},
				isOptional: true,
				editable: function(){
					return new $.Form.FormLayout({
						skipOnDisabled: true,
						items:[
							{
								name: 'coordinates',
								item: new $.Form.FormLayout({
									items: [{
										name: 'latitude',
										item: new $.Form.Number({
											validators: [$.Form.validator.NotEmpty],
											placeholder: "latitude"
										})
									},{
										name: 'longitude',
										item: new $.Form.Number({
											validators: [$.Form.validator.NotEmpty],
											placeholder: "longitude"
										})
									}]
								}),
								checkable: true
							},{
								name: 'place',
								item: new $.Form.Text({
									validators: [$.Form.validator.NotEmpty],
									placeholder: "place"
								}),
								checkable: true
							},{
								name: 'floor',
								item: new $.Form.Number({
									validators: [$.Form.validator.NotEmpty],
									placeholder: "floor"
								}),
								checkable: true
							},{
								name: 'room',
								item: new $.Form.Text({
									validators: [$.Form.validator.NotEmpty],
									placeholder: "room"
								}),
								checkable: true
							}
						],
						format: {
							'out': function(value){
								if($.isPlainObject(value) && !$.isEmptyObject(value)){
									var o = $.extend({},value, value.coordinates);
									delete o.coordinates;
									return o;
								}
								return null;
							},
							'in': function(value){
								if($.isPlainObject(value) && !$.isEmptyObject(value)){
									var o = $.extend({},value);
									if( typeof o.latitude != 'undefined' && typeof o.longitude != 'undefined'){
										o.coordinates = {
											latitude: o.latitude,
											longitude: o.longitude
										};
										delete o.latitude;
										delete o.longitude;
									}
									return o;
								} else return {};
							}
						}
					});
				}
			}
		}
	}
}))