(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','bootstrap-select','bootstrap-toggle'], factory);
    } else {
        // Browser globals
        factory(root.jQuery);
    }
}(this, function ($) {
	
	'use strict';
	
	
	
	
	var scopes = [
		{
			'name': 'resource',
			'label' :'resources access',
			'description': '<b>read</b>: read the content of any resource<br><b>write</b>: create resources of any kind and modify the content of any resource<br><b>admin</b>: modify resource properties, delete resource and access to apikeys',
			'values' : {
				'read': 'resource:read',
				'write': 'resource:write',
				'admin': 'resource:admin'
			}
		},
		{
			'name': 'file',
			'label' :'files access',
			'description': '<b>read</b>: read the content of any file<br><b>write</b>: create files and modify the content of any file',
			'values' : {
				'read': 'file:read',
				'write': 'file:write'
			}
		},
		{
			'name': 'table',
			'label' :'table access',
			'description': '<b>read</b>: read the content of any table<br><b>write</b>: create tables and modify the content of any table<br><b>append</b>: append data to any existing table',
			'values' : {
				'read': 'table:read',
				'write': 'table:write',
				'append': 'table:append'
			}
		},
		{
			'name': 'device',
			'label' :'devices access',
			'description': '<b>read</b>: send GET request to any device<br><b>write</b>: send POST,PUT,PATCH,DELETE request to any device',
			'values' : {
				'read': 'device:read',
				'write': 'device:write'
			}
		},
		{
			'name': 'app',
			'label' :'apps access',
			'description': '<b>read</b>: read the raw script content of any apps<br><b>write</b>: create and edit apps<br><b>execute</b>: execute apps',
			'values' : {
				'read': 'app:read',
				'write': 'app:write',
				'execute': 'app:execute'
			}
		},
		{
			'name': 'settings',
			'label' :'settings access',
			'description':'<b>read</b>: read the settings<br><b>write</b>: modify the settings',
			'values' : {
				'read': 'settings:read',
				'write': 'settings:write'
			}
		},
		{
			'name': 'notification',
			'label':'send notification'
		},
		{
			'name': 'rule',
			'label' :'rules management',
			'description':'<b>read</b>: read rules attributes<br><b>write</b>: create rules<br><b>execute</b>: execute rules<br><b>admin</b>: delete rules',
			'values' : {
				'read': 'rule:read',
				'write': 'rule:write',
				'execute': 'rule:execute',
				'admin': 'rule:admin'
			}
		}
	];
	
	
	
	var advancedPermission = ['file','table','device','app'];
	
	
	var ScopeForm = function(element, options) {

        var defaults = {
			value: ""
        }

        var plugin = this;

        plugin.settings = {}

        var $element = $(element),
             element = element;
			
		
		var advancedState = false,
			showAdvanced = function(){
				if(!advancedState){
					$advancedItems.show();
					advancedState = true;
				}
			},
			hideAdvanced = function(){
				if(advancedState){
					$advancedItems.hide();
					advancedState = false;
				}
			},
			$advancedItems = null;
		

        plugin.init = function() {
            plugin.settings = $.extend({}, defaults, options);
			
			$element.empty();
			
			// build the dom
			var $table = $('<table class="table">').appendTo($element);
			var $tbody = $('<tbody>').appendTo($table);
			scopes.forEach(function(scope){
				
				var $select = null;
				
				if(scope.values){
					$select = $('<select class="selectpicker form-control" multiple>');
					for(var key in scope.values){
						$select.append('<option value="'+scope.values[key]+'">'+key+'</option>');
					}
				}
				else {
					$select = $('<div class="checkbox checkbox-slider--b-flat"><label><input type="checkbox"><span></span></label></div>');
				}
				
				var $info = scope.description ? $('<span class="glyphicon glyphicon-question-sign" aria-hidden="true"></span>').popover({
					content: scope.description || '',
					delay: 200,
					placement: 'top',
					trigger: 'hover',
					html: true
				}) : null;
				
				$('<tr data-scope="'+scope.name+'">').append(
					$('<td>').append(scope.label,' ',$info).css('vertical-align','middle'),
					/*$('<td>').append($info),*/
					$('<td>').append($select)
				).appendTo($tbody);
				
				
			})
			
			$tbody.find('select.selectpicker').selectpicker({
				noneSelectedText: 'no access'
			});
			
			$advancedItems = $tbody.find('tr').filter(function(){
				return advancedPermission.indexOf( $(this).attr('data-scope').split(':').shift() ) !== -1 ;
			}).hide();
			
			var $advancedBtn = $('<button type="button" class="btn btn-link">advanced permissions</button>').click(function(){
					advancedState ? hideAdvanced() : showAdvanced();
				}),
				$resourceItem = $tbody.find('tr[data-scope="resource"]').after( $('<tr>').html($('<td colspan="3">').html($advancedBtn)) );
			
			$advancedItems.children('td:first-child').prepend('<span class="glyphicon glyphicon-hand-right" aria-hidden="true" style="margin: 0 10px;"></span>');
			
			setValue(plugin.settings.value);
			
        }

        plugin.value = function(value) {
            // No value passed, act as a getter.
			if ( value === undefined ) {
				return getValue();
	
			// Value passed, act as a setter.
			} else {
				setValue(value);
			}
        }
		
		var setValue = function(scopeString){
			var advanced = false;
			
			if(typeof scopeString != 'string')
				scopeString = '';
			
			// reset all permissions
			$element.find('tr select').selectpicker('val',[]);
			$element.find('tr input[type="checkbox"]').prop('checked',false);
			
			// set permissions
			scopeString.split(" ").forEach(function(scope){
				
				var type = scope.split(':').shift();
				
				if(!advanced && advancedPermission.indexOf(type) !== -1) advanced = true;
				
				for(var i =0; i<scopes.length; i++){
					var scopeObj = scopes[i];
					if(scopeObj.name == type){
						
						if(scopeObj.values){
							var $e = $element.find('tr[data-scope="'+scopeObj.name+'"] select');
							$e.selectpicker('val', ($e.val()||[]).concat(scope));
						}
						else {
							$element.find('tr[data-scope="'+scopeObj.name+'"] input[type="checkbox"]').prop('checked',true);
						}
						
						break;
					}
				}
				
			});
			
			advanced ? showAdvanced() : hideAdvanced();
		}
		
		var getValue = function(){
			var permissions = [];
			
			$element.find('tr input[type="checkbox"]').each(function(){
				
				var $this = $(this),
					scope = $this.closest('tr').attr('data-scope'),
					checked = $this.prop('checked');
				if(checked) permissions.push(scope);
			});
			
			$element.find('tr select').each(function(){
				var $this = $(this),
					type = $this.closest('tr').attr('data-scope'),
					values = $this.val() || [];
				
				// skip advanced values if not visible
				if(advancedPermission.indexOf(type) !== -1 && !advancedState) return;
				
				permissions = permissions.concat(values);
			});
			
			return permissions.join(' ');
		}

        plugin.init();

    }
	
	/* register as a plugin in jQuery */
	$.fn.scopeForm = function(){
		var args = [].slice.call(arguments);
		
		if (this[0]) { // this[0] is the renderTo div
			
			var instance = $(this[0]).data('scopeForm');
			
			if(instance){
				if(args.length){
					if(typeof args[0] == 'string'){
						// access the attribute or method
						var prop = instance[args.shift()];
						if(typeof prop == 'function'){
							var r = prop.apply(instance,args);
							return (r === instance) ? this : r; // make it chainable
						}
						else {
							if(args.length==0){
								// getter
								return prop;
							}
							else if(args.length==1){
								// setter
								prop = args[0];
								return this;
							}
						}
					}
				}
				else
					return instance;// When called without parameters return the instance
			}
			
			// if we are are, it means that there is no instance or that the user wants to create a new one !
			// /!\ NOTE : be sure to not emit any event in the constructor, or delay them using the setTimeout function !
			instance = new ScopeForm(this[0],args[0],args[1],args[2],args[3],args[4],args[5],args[6]);
			$(this[0]).data('scopeForm',instance);
			
			return this;
		}
	};
	
	
	
}));
