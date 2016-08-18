(function(){
	'use strict';
	
	/*
		$('<div>').ScopeWizard({
			resource: myDevice
		});
	*/
	
	
	
	
	var scopes = [
		{
			'name': 'resource',
			'label': 'resources global access',
			'description':'<b>write</b>: Full, permissive scope to access all of a user\'s resources. Request this scope only when it is strictly necessary.<br><b>read only</b>: Allows read-only access to any resource metadata and content.',
			'values':{
				'write': "resource",
				'read only': "resource.readonly",
				'deny': ''
			}
		},
		{
			'name': 'resource.owndata',
			'label': 'own resource',
			'description':'Allow this device to create resources and to read/write only those resources.',
			'values':{
				'allow': "resource.owndata",
				'deny': ''
			}
		},
		{
			'name': 'notification',
			'label': 'notification',
			'description':'Allow to send notification.',
			'values':{
				'allow': "notification",
				'deny': ''
			}
		},
		{
			'name': 'profile',
			'label': 'profile',
			'description':'<b>write</b>: View an modify your profile. Request this scope only when it is strictly necessary.<br><b>read only</b>: View your basic profile info.',
			'values':{
				'write': "profile",
				'read only': "profile.readonly",
				'deny': ''
			}
		}
	];
	
	
	
	function findScope(scope){
		if(typeof scope == 'string' && scope.length)
			for(var i=0; i<scopes.length; i++)
				for(var j in scopes[i].values)
					if(scopes[i].values[j] === scope)
						return scopes[i];
	}
	
	
	var ScopeWizard = function(element, options) {

        var defaults = {
			value: ""
        }

        var plugin = this;

        plugin.settings = {}

        var $element = $(element),
             element = element;

        plugin.init = function() {
            plugin.settings = $.extend({}, defaults, options);
			
			$element.empty();
			
			// build the dom
			var $table = $('<table class="table">').appendTo($element);
			var $tbody = $('<tbody>').appendTo($table);
			scopes.forEach(function(scope){
				
				var $select = $('<select class="form-control">');
				for(var accessName in scope.values){
					$select.append('<option value="'+scope.values[accessName]+'">'+accessName+'</option>');
				}
				
				var $info = $('<button class="btn btn-default"><span class="glyphicon glyphicon-question-sign" aria-hidden="true"></span></button>').popover({
					content: scope.description || '',
					delay: 0,
					placement: 'top',
					trigger: 'focus',
					html: true
				});
				
				$('<tr data-scope="'+scope.name+'">').append(
					$('<td>').append(scope.label).css('vertical-align','middle'),
					$('<td>').append($info),
					$('<td>').append($select)
				).appendTo($tbody);
			})
			
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
			if(typeof scopeString != 'string')
				return '';
			
			// reset all the permissions:
			$element.find('select').val('');
			
			// set the scope if any
			var validScopeList = [];
			scopeString.split(" ").forEach(function(scopeId){
				var scope = findScope(scopeId);
				if(scope){
					/*console.log('toto');
					console.log(scopeId);
					console.log(scope);
					console.log($element.find('tr[data-scope="'+scope.name+'"]').find('select'));*/
					$element.find('tr[data-scope="'+scope.name+'"]').find('select').val(scopeId);
					validScopeList.push(scopeId);
				}
			});
			
			return validScopeList.join(' ');
		}
		
		var getValue = function(){
			return $element.find('select').map(function () { return $(this).val(); }).get().join(' ');
		}

        plugin.init();

    }
	
	/* register as a plugin in jQuery */
	if (window.jQuery)
		window.jQuery.addPlugin('ScopeWizard',ScopeWizard);
	
	
})();
