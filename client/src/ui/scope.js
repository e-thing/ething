(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define([], factory);
    }
}(this, function () {
	
	var UI = window.UI = window.UI || {};
	
	
	var scopes = {
		'resource:read': 'read the content of any resource',
		'resource:write': 'create resources of any kind and modify the content of any resource',
		'resource:admin' : 'modify resource properties, delete resource and access to apikeys',
		'file:read' : 'read the content of any file',
		'file:write': 'create files and modify the content of any file',
		'table:read' : 'read the content of any table',
		'table:write' : 'create tables and modify the content of any table',
		'table:append' : 'append data to any existing table',
		'app:read' : 'read the raw script content of any apps',
		'app:write' : 'create and edit apps',
		'app:execute' : 'execute apps',
		'device:read' : 'send GET request to any device',
		'device:write' : 'send POST,PUT,PATCH,DELETE request to any device',
		'notification' : 'send notification',
		'settings:read' : 'read the settings',
		'settings:write' : 'modify the settings',
		'proxy:read' : 'send GET request through your local network',
		'proxy:write' : 'send POST,PUT,PATCH,DELETE through your local network'
	};
	
	
	UI.scopes = scopes;
	
	return UI;
	
}));