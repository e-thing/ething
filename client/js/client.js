(function(){
	
	
	
	
	var url_re = new RegExp('^([a-z]+:\\/\\/)?'+ // protocol
			'((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
			'((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
			'(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
			'(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
			'(\\#[-a-z\\d_]*)?$','i'); // fragment locator
		
	
	var properties = [
		
		/*
		
		"property":{
			name: "foo", // the name of this property
			label:"name displayed for that property" (default: property's name),
			get:"name of the accessor in the resource object" (default: property's name),
			onlyForType:[], this property is only avalable for the specified types
			notForType:[], this property is not avalable for the specified types
			formatter:function(value){return value;}, value formatter
			default: print the default value for undefined value
			editable:false || form describing object
		}
		
		*/
		
		{
			name: "name",
			editable:{
				input: 'text',
				get: function($e){
					var v = $e.val().trim();
					if(v.length==0)
						throw "The name must not be empty";
					return v;
				}
			}
		},
		
		{
			name: "type",
		},
		{
			name: "user",
			label: "owner",
			formatter: function(user){
				return user ? (user.id()==EThing.auth.getUser().id() ? 'Me' : user.name()) : null;
			}
		},
		{
			name: "createdBy",
			label: "created by",
			formatter: function(id){
				var v = id;
				if(EThing.arbo.isLoaded()){
					v = EThing.arbo.findOneById(id);
					if(v)
						v = createdByRess.basename();
				}
				return v ? v : 'Me';
			}
		},
		{
			name: "createdDate",
			label: "created",
			get: "ctime",
			formatter: EThing.utils.dateToString
		},
		{
			name: "modifiedDate",
			label: "modified",
			get: "mtime",
			formatter: EThing.utils.dateToString
		},
		{
			name: "lastSeenDate",
			onlyForType: ['Device'],
			label: "last seen",
			formatter: function(date){
				return date ? EThing.utils.dateDiffToString( Math.floor( (Date.now() - date.getTime()) / 1000 ) ) : 'never';
			}
		},
		{
			name: "size",
			formatter: EThing.utils.sizeToString,
			default: 0
		},
		{
			name: "mime",
			onlyForType: ['File'],
		},
		{
			name: "length",
			label: "rows",
			onlyForType: ['Table'],
			default: 0
		},
		{
			name: "maxLength",
			label: "max rows",
			onlyForType: ['Table'],
			formatter: function(v){
				return v ? String(v) : "none";
			},
			isOptional: true,
			editable:{
				input: 'number',
				get: function($e){
					return parseInt($e.val());
				},
				attr: {
					'min':1
				}
			}
		},
		{
			name: "expireAfter",
			label: "expire after",
			formatter: function(v){
				return v ? EThing.utils.dateDiffToString(v) : "none";
			},
			isOptional: true,
			editable: function(){
				return new $.Form.Duration({
					minute: false,
					hour: true,
					day: true
				});
			}
		},
		{
			name: "icon",
			onlyForType: ['App'],
			isOptional: true,
			get: function(r){
				return r.iconLink(true);
			},
			editable: function(r){
				return new $.Form.Image({
					onChange: function(blob){
						if(blob && blob.size>64000)
							throw 'Only image with a size lower than 64Kb is accepted';
					},
					transform: $.Form.File.toBase64
				});
			}
		},
		{
			name: "battery",
			onlyForType: ['Device'],
			formatter: function(batValue){
				return (typeof batValue == 'number') ? batValue+"%" : null;
			}
		},
		{
			name: "url",
			category: 'Server',
			onlyForType: ['Device'],
			formatter: function(v){
				if(typeof v == 'string'){
					var href = v;
					if(!/^http:\/\//i.test(v))
						href= "http://"+v;
					return '<a href="'+href+'" target="_blank">'+v+'</a>';
				}
			},
			editable:{
				input: 'url',
				get: function($e){
					var url = $e.val().trim();
					if(!url_re.test(url)) throw 'invalid URL';
					return url;
				},
				attr:{
					placeholder: "scheme://hostname:port/path"
				}
			}
		},
		{
			name: "auth",
			label: 'authentication',
			category: 'Server',
			onlyForType: ['Device'],
			formatter: function(v){
				if(v){
					return v.user+':***';
				}
			},
			isOptional: true,
			editable: {
				input: function(){
					return $('<div>').form(new $.Form.FormLayout([{
						label: 'type',
						item: {
							input: ['basic','digest']
						}
					},{
						label: '_',
						item: '<input type="text" name="user_f5f7tyjh"/><input type="password" name="pass_f5f7tyjh"/>',
						hidden: true,
						skip: true
					},{
						label: 'user',
						item: {
							input: '<input type="text" placeholder="user" autocomplete="off">',
							validator: $.Form.validator.NotEmpty
						}
					},{
						label: 'password',
						item: {
							input: '<input type="password" placeholder="password" autocomplete="off">',
							validator: $.Form.validator.NotEmpty
						}
					}]));
				}
			}
		},
		{
			name: "description",
			editable: {
				input: function(){
					return '<textarea rows="3">';
				}
			}
		},
		{
			name: "location",
			formatter: function(v){
				if(v){
					return v.latitude+"N "+v.longitude+"E";
				}
			},
			isOptional: true,
			editable: {
				input: function(){
					return $('<div>').form({
						latitude: {
							input: '<input type="number" placeholder="latitude">',
							validator: $.Form.validator.NotEmpty
						},
						longitude: {
							input: '<input type="number" placeholder="longitude">',
							validator: $.Form.validator.NotEmpty
						}
					});
				}
			}
		},
		{
			name: "rules",
			notForType: ['App'],
			formatter: function(rules){
				return (!rules || !rules.length) ? null : (rules.length+' rule(s)');
			},
			editable:function(resource){ // new context
				return {
					input: function(){
						var $input = $('<div>').text('loading...');
						this.dfr = EThing.utils.require(["css/lib/rule.css","js/lib/rule.js"],function(){
							$input.empty().ruleWizard({
								parent: resource
							});
						})
						return $input;
					},
					set: function($e,v){
						this.dfr.done(function(){
							$e.ruleWizard('value',v)
						});
					},
					get: function($e){
						return this.dfr.then(function(){
							return $e.ruleWizard('value');
						});
					}
				};
			}
		},
		{
			name: "scope",
			label: 'permission',
			onlyForType: ['Device'],
			formatter: function(){
				return null;
			},
			editable:{
				input: function(){
					var $input = $('<div>').text('loading...');
					this.dfr = EThing.utils.require("js/lib/scope.js",function(){
						$input.empty().scopeWizard();
					})
					return $input;
				},
				set: function($e,v){
					this.dfr.done(function(){
						$e.scopeWizard('value',v)
					});
				},
				get: function($e){
					return this.dfr.then(function(){
						return $e.scopeWizard('value');
					});
				}
			},
			'default': 'resource.owndata notification'
		},
		{
			name: "descriptor",
			category: 'Server',
			label: 'api',
			get: null, // only editable
			onlyForType: ['Device'],
			editable:function(resource){
				
				return {
					input: function(){
						var $input = $('<div class="descriptor-overview">loading...</div>');
							
						$input.on('editor-loaded.tv',function(){
							$(this).textViewer('editor').setSize(null,'400px');
						});
						
						var tvopt = {
							toolbar: {
								enable: true,
								filename: {
									enable: false
								}
							},
							lint: true,
							mode: 'application/json',
							actions: {
								'open': {
									enable: false
								},
								'save': {
									enable: false
								},
								'saveas': {
									enable: false
								},
								'mode':{
									enable: false
								},
								'fullscreen':{
									enable: true
								}
							}
						};
						
						if((resource instanceof EThing.Device) && resource.url()){
							$input.textViewer($.extend(true,tvopt,{
								data: EThing.Device.getDescriptor(resource,true)
							}));
						}
						else {
							// default
							$input.textViewer($.extend(true,tvopt,{
								data: JSON.stringify({
										"swagger": "2.0",
										"info": {
											"version": "0.0.0",
											"title": "<enter your title>"
										},
										"paths": {}
									},null,2),
							}));
						}
						
						$input.addClass('embedded');
						
						
						$input.on('before-trigger-fullscreen.tv',function(){
							// some hack on textviewer inside bootstrap modal dialogs due to 'transform' css property
							var isFullscreen = $(this).textViewer('isFullscreen');
							$(this).parents('.modal-dialog').css({
								'transform': isFullscreen ? '' : 'initial',
								'transition': isFullscreen ? '' : 'none'
							});
							// in fullscreen, no 
							$(this).textViewer('editor').setSize(null,isFullscreen ? '400px' : '100%');
						});
						
						return $input;
					},
					// content is set on input function
					set: null,
					get: function($input){
						var json = $input.textViewer('value'),
							spec = JSON.parse(json);
						
						if(spec.hasOwnProperty('host'))
							throw 'the host property must not be set';
						if(spec.hasOwnProperty('schemes'))
							throw 'the schemes property must not be set';
						
						return spec;
					}
				};
			}
		}
	];
	
	// set default to properties:
	for(var i=0; i<properties.length; i++)
		properties[i] = $.extend({
			label:properties[i].name,
			get:properties[i].name,
			condition:true,// the condition to tell if this property is enable or not
			onlyForType: null,
			notForType:[],
			formatter: null,
			//default: undefined
			editable:null
		},properties[i]);
	
	
	function getResourceProperties(resource, extendProps, filter){
		var out = [],
			resourceType = (resource instanceof EThing.Resource) ? resource.type() : resource,
			undefined;
		
		for(var i=0; i<properties.length; i++){
			
			var property = $.extend(true, {
				resource: (resource instanceof EThing.Resource) ? resource : null,
				resourceType: resourceType
			}, properties[i], ($.isPlainObject(extendProps) && extendProps.hasOwnProperty(properties[i].name)) ? extendProps[properties[i].name] : null);
			
			var condition = property.condition;
			if(typeof condition == 'function')
				condition = condition.call(property);
			if(!condition)
				continue;
			
			if(Array.isArray(filter) && filter.indexOf(property.name) === -1)
				continue; // show only properties listed in the argument 'properties'.
			
			if((typeof filter == 'function') && !filter.call(property,property,resource))
				continue;
			
			
			if(
				$.inArray(resourceType,property.notForType)==-1 &&
				(!property.onlyForType || $.inArray(resourceType,property.onlyForType)>=0)
			){
				
				var value = undefined,
					hasDefaultValue = (typeof property.default != 'undefined');
				
				// get the value
				if(resource instanceof EThing.Resource){
					if(typeof property.get == 'function')
						value = property.get.call(property,resource);
					else if(typeof property.get == 'string'){
						var accessor = EThing[resourceType].prototype[property.get];
						if(typeof accessor == "undefined")
							continue;
						value = (typeof accessor == 'function') ? accessor.call(resource) : accessor;
					}
				}
				
				if(typeof value == "undefined"){
					if(hasDefaultValue)
						value = property.default;
				}
				
				if(typeof value != "undefined"){
					property.value = value;
					if(typeof property.formatter == 'function')
						property.formattedValue = property.formatter.call(property,value);
					else
						property.formattedValue = value;
				}
				
				if(typeof property.label == 'function')
					property.label = property.label.call(property);
				
				out.push(property);
				
			}
		}
		return out;
	}
	
	function getResourceProperty(resource, property){
		return getResourceProperties(resource,null,[property]).shift();
	}
	
	function getResourceFormattedValues(resource, extendProps, filter){
		var pps = getResourceProperties(resource,extendProps,filter),
			out = {};
		
		for(var i=0; i<pps.length; i++){
			var property = pps[i];
			if((typeof property.formattedValue != 'undefined') && property.formattedValue !== null)
				out[property.label] = property.formattedValue;
		}
		
		return out;
	}
	
	
	function getResourceForm(resource, extendProps, filter){
		var pps = getResourceProperties(resource,extendProps,filter),
			out = [],
			undefined;
		
		for(var i=0; i<pps.length; i++){
			
			var property = pps[i],
				editObj = typeof property.editable == 'function' ? property.editable.call(property,resource) : property.editable;
			
			if(editObj){
				var value = undefined;
				
				if(property.hasOwnProperty('value'))
					value = property.value;
				
				if(typeof value != 'undefined' && editObj instanceof $.Form.Item)
					editObj.setValue(value);
				
				out.push($.extend(true,{
					label: property.label,
					name: property.name,
					checkable: !!property.isOptional,
					checked: !!(value),
					item: {
						value: value,
						name: property.name
					}
				},{
					item: editObj
				}));
				
			}
			
		}
		
		return out;
	}
	
	
	
	
	
	var edit = function(resource, target){
		var win = window.open('editor.html?r=' + resource.id(), target || '_self' );
		win.focus();
	}
	

	// open a modal dialog to change settings of a resource
	var settings = function(resource, callback){
		
		var formItem, categories = {};
		
		// tidy up by categories
		getResourceProperties(resource).forEach(function(property){
			var category = property.category || 'General';
			if(!categories.hasOwnProperty(category))
				categories[category] = [];
			categories[category].push(property.name);
		});
		
		if(Object.keys(categories).length > 1){
			// multiple tabs
			var tabArgs = [];
			for(var cat in categories){
				var item;
				
				// special case
				if( (resource instanceof EThing.Device) && /server/i.test(cat) ){
					item = new $.Form.FieldsEnabler({
						label: 'Enable',
						item: new $.Form.FormLayout(getResourceForm(resource, null, categories[cat])),
						value: !!resource.url()
					});
				}
				else
					item = new $.Form.FormLayout(getResourceForm(resource, null, categories[cat]));
				
				tabArgs.push({
					name: cat,
					item: item
				});
			}
			formItem = new $.Form.TabsLayout({merge: true, items: tabArgs});
		}
		else {
			formItem = new $.Form.FormLayout(getResourceForm(resource));
		}
		
		
		$.FormModal({
			item: formItem,
			title: 'Editing the '+resource.type()+' "'+resource.name()+'"',
			validLabel: '+Apply',
			resource: resource
		},function(props){
			return resource.set(props).done(function(){
				if(typeof callback == 'function')
					callback.call(this,props);
			});
		});
		
	}
	
	
	
	
	
	
	var createApp = function(callback){
		
		var $code = $('<div class="subpart subpart-primary" name="code">'+
		  '<h4>Build from source code</h4>'+
		  '<p>Enter below the name of the application you want to develop. Then you will be able to write your own application in an editor.</p>'+
		  '<p>'+
			'<div class="input-group">'+
			  '<input type="text" class="form-control" placeholder="Application name...">'+
			  '<span class="input-group-btn">'+
				'<button class="btn btn-primary" type="button">Edit</button>'+
			  '</span>'+
			'</div>'+
		   '</p>'+
		'</div>');
		var $repository = $('<div class="subpart subpart-primary" name="repository">'+
		  '<h4>Install from a GitHub repository</h4>'+
		  '<p>Enter below the repository URL of the application you want to install. The repository must contains an index.html file.</p>'+
		  '<p>'+
			'<div class="input-group">'+
			  '<input type="text" class="form-control" placeholder="https://github.com/.../...">'+
			  '<span class="input-group-btn">'+
				'<button class="btn btn-primary" type="button">Install</button>'+
			  '</span>'+
			'</div>'+
		   '</p>'+
		'</div>');
		
		$.getJSON('/ething/lib/examples/meta.json',function(examples){
			var $example = $('<div class="subpart subpart-primary" name="example">'+
			  '<h4>Install an example</h4>'+
			  '<p>Select below the example you want to install.</p>'+
			  '<p>'+
				'<div class="input-group">'+
				  '<select class="form-control"></select>'+
				  '<span class="input-group-btn">'+
					'<button class="btn btn-primary" type="button">Install</button>'+
				  '</span>'+
				'</div>'+
			   '</p>'+
			'</div>');
			
			$example.find('button').click(function(){
				var exampleName = $select.val(), example = null;
				if(!exampleName) return;
				for(var i=0; i<examples.length; i++){
					if(examples[i].name === exampleName){
						example = examples[i];
						break;
					}
				}
				if(!example) return;
				// get content
				$.get('/ething/lib/examples/'+example.name+'.html',null,null,'text').done(function(content){
					create(example.name,content,$example);
				})
				
			});
			
			var $select = $example.find('select');
			examples.forEach(function(example){
				$('<option>'+example.name+'</option>').appendTo($select);
			});
			
			if(examples.length){
				$html.append($example);
			}
		});
		
		
		
		
		var $html = $('<div>').append($code,$repository);
		
		var setError = function(message, tag){
			var $sp = (typeof tag == 'string') ? $('div.subpart[name="'+tag+'"]',$html) : tag;
			if(!message){
				// remove any error
				$sp.find('.alert').remove();
				$sp.find('.input-group').removeClass('has-error');
			}
			else {
				//set error
				var $err = $sp.find('.alert');
				if(!$err.length)
					$err = $('<div class="alert alert-danger" role="alert">').appendTo($sp);
				$err.html(message);
				$sp.find('.input-group').addClass('has-error');
			}
		}
		
		// bind enter key pressed 
		$html.find('input[type="text"]').keypress(function(event) {
			var keycode = (event.keyCode ? event.keyCode : event.which);
			if (keycode == 13) {
				$(this).parent().find('button').trigger('click');
			}
		});
		
		
		function create(name,content,$h){
			
			EThing.App.create({
				name: name,
				content: btoa(content)
			},function(app){
				if(app instanceof EThing.App){
					// the creation was successfull
					$html.modal('hide');// will be autoremoved
					if(EThing.arbo.isLoaded())
						EThing.arbo.add(app);
					
					if(typeof callback == 'function')
						callback.call(app,$h.attr('name'));
				}
				else
					// print the error message but do not close the modal dialog
					setError(app.message,$h);
			});
			
		};
		
		
		$repository.find('button').click(function(){
			
			var url = $('input',$repository).val().trim(),
				gitUrlValidator = /^(https?:\/\/)?github.com\/[-a-zA-Z\d%_.~+]+\/[-a-zA-Z\d%_.~+]+$/;
			
			if(!gitUrlValidator.test(url)){
				setError('Invalid Github URL.',$repository);
				return;
			}
			
			var rawBaseUrl = url.replace(/^(https?:\/\/)?github.com/,'https://raw.githubusercontent.com'),
				name = url.replace( /.*\//, '' );
			
			// index.html url (https://raw.githubusercontent.com/<Owner>/<Package>/master/index.html)
			var indexUrl = rawBaseUrl+'/master/index.html';
			
			$.get(indexUrl)
				.done(function(content){
					
					create(name,content,$repository);
					
				})
				.fail(function(){
					setError('Could not find any index.html file in the master branch.',$repository);
				});
			
		});
		
		$code.find('button').click(function(){
			
			var name = $('input',$code).val().trim();
			
			if(!name){
				setError('empty or invalid name',$code);
				return;
			}
			
			// install this app with a default content
			
			$.ajax({
				url: 'app.default.txt',
				dataType: 'text'
			})
			.done(function(defaultContent){
				create(name,defaultContent,$code);
			})
			.fail(function(){
				create(name,null,$code);
			});
			
		});
		
		$html
			.modal({
				title: '<span class="glyphicon glyphicon-flash" aria-hidden="true"></span> Add a new application'
			})
		
		return;
	}
	
	var createDevice = function(callback){
		$.FormModal({
			item: new $.Form.TabsLayout({
				merge: true,
				items: [{
					name: 'general',
					item: new $.Form.FormLayout(getResourceForm('Device', null, ['name','scope','location','description']))
				}, {
					name: 'server',
					item: new $.Form.FieldsEnabler({
						label: 'Enable',
						item: new $.Form.FormLayout(getResourceForm('Device', null, ['url','auth','descriptor'])),
						value: false
					})
				}]
			}),
			title: '<span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Create a new Device',
			validLabel: '+Add'
		},function(props){
			return EThing.Device.create(props).done(function(r){
				// the creation was successful, close the dialog and reload
				if(EThing.arbo.isLoaded())
					EThing.arbo.add(r);
				
				if(typeof callback == 'function')
					callback.call(r);
			});
		});
	}
	
	var createFile = function(callback, dir){
	
		var formEntries = getResourceForm('File', null, ['name','description']);
		
		formEntries.push({
			label: 'content',
			item: new $.Form.File({
				onChange: function(input){
					var nameItem = this.form().findItem('name');
					if(input.files && input.files[0] && nameItem && !nameItem.getValue())
						nameItem.setValue(input.files[0].name);
				},
				transform: $.Form.File.toBase64,
				title: '<span class="glyphicon glyphicon-open" aria-hidden="true"></span> import a local file',
				allowEmpty: true
			})
		});
		
		$.FormModal({
			item: new $.Form.FormLayout(formEntries),
			title: '<span class="glyphicon glyphicon-file" aria-hidden="true"></span> Create a new File',
			validLabel: '+Add'
		},function(props){
			
			if(dir instanceof EThing.Folder && dir.name().length && props.name){
				props.name = dir.name()+'/'+props.name;
			}
			
			var dfr = EThing.File.create(props).done(function(r){
				// the creation was successful, close the dialog and reload
				if(EThing.arbo.isLoaded())
					EThing.arbo.add(r);
				
				if(typeof callback == 'function')
					callback.call(r);
			});
			
			Uploader.UI.add(EThing.Resource.basename(props.name),dfr);
			
		});
		
	}
	
	// table import helpers
	function parseCSV(content,delimiter,limit){
		
		// Check to see if the delimiter is defined. If not,
		// then default to comma.
		if(!delimiter){
			if(!(delimiter = getCsvDelimiter(content))) // auto determine
				throw 'invalid CSV content';
		}

		// Create a regular expression to parse the CSV values.
		var objPattern = new RegExp(
			(
				// Delimiters.
				"(\\" + delimiter + "|\\r?\\n|\\r|^)" +

				// Quoted fields.
				"(?:\"([^\"]*(?:\"\"[^\"]*)*)\"|" +

				// Standard fields.
				"([^\"\\" + delimiter + "\\r\\n]*))"
			),
			"gi"
		);


		// Create an array to hold our data. Give the array
		// a default empty first row.
		var arrData = [[]];

		// Create an array to hold our individual pattern
		// matching groups.
		var arrMatches = null;


		// Keep looping over the regular expression matches
		// until we can no longer find a match.
		var line = 0, prevEmptyField = false;
		while (arrMatches = objPattern.exec( content )){
			
			// Get the delimiter that was found.
			var strMatchedDelimiter = arrMatches[ 1 ];

			// Check to see if the given delimiter has a length
			// (is not the start of string) and if it matches
			// field delimiter. If id does not, then we know
			// that this delimiter is a row delimiter.
			if (
				strMatchedDelimiter.length &&
				strMatchedDelimiter !== delimiter
				){
				
				if(prevEmptyField)
					arrData[ arrData.length - 1 ].pop();
				
				line++;
				
				if(limit && line>=limit)
					break;
				
				// Since we have reached a new row of data,
				// add an empty row to our data array.
				arrData.push( [] );

			}
			
			prevEmptyField = false;
			
			var strMatchedValue;

			// Now that we have our delimiter out of the way,
			// let's check to see which kind of value we
			// captured (quoted or unquoted).
			if (arrMatches[2]){

				// We found a quoted value. When we capture
				// this value, unescape any double quotes.
				strMatchedValue = arrMatches[ 2 ].replace(
					new RegExp( "\"\"", "g" ),
					"\""
					);

			} else {

				// We found a non-quoted value.
				if(/^\s*[-+]?\d*\.?\d+([eE][-+]?\d+)?\s*$/.test(arrMatches[ 3 ])){
					// number
					strMatchedValue = parseFloat(arrMatches[ 3 ]);
				}
				else if(/^\s*(true|false)\s*/i.test(arrMatches[ 3 ])){
					// boolean
					strMatchedValue = /true/i.test(arrMatches[ 3 ]);
				}
				else {
					// string
					strMatchedValue = arrMatches[ 3 ];
					if(/^\s*$/.test(strMatchedValue))
						prevEmptyField = true;
				}

			}


			// Now that we have our value string, let's add
			// it to the data array.
			arrData[ arrData.length - 1 ].push( strMatchedValue );
			
		}
		
		
		// Return the parsed data + remove empty lines
		return arrData.filter(function(d){
			return d.length>0;
		});
		
	}
	
	function getCsvDelimiter(content){
		var delimiters = [',', ';', '\t', '|', ':'], best, colmax=0;
		
		for(var i=0; i<delimiters.length; i++){
			
			// return the number of columns or false if an error occurs
			var ncol = parseCSV(content,delimiters[i],5).reduce(function(ncol, fields, index, array){
				if(index===0)
					ncol = fields.length;
				return (ncol===false || ncol != fields.length) ? false : ncol;
			},false);
			
			if(ncol!==false && ncol>colmax){
				best = delimiters[i];
				colmax = ncol;
			}
			
		}
		
		return best;
	}
	
	function readCSV(content){
		var data = parseCSV(content), out = [];
		
		// first line is the field's name
		var fields = data.shift();
		
		for(var i=0; i<data.length; i++){
			var d = {};
			for(var j=0; j<fields.length && j<data[i].length; j++)
				d[fields[j]] = data[i][j];
			out.push(d);
		}
		
		return out;
	}
	
	var createTable = function(callback, dir){
		
		var formEntries = getResourceForm('Table', null, ['name','description']),
			csvExt = ['csv','tsv','tab','txt'],
			jsonExt = ['json'];
		
		if (window.File && window.FileReader && window.FileList && window.Blob){
			
			var data_ = null, loading_ = false;
			
			formEntries.push({
				label: 'content',
				item: {
					input: function(){
						var self = this;
						
						var $btn = $('<button class="btn btn-default"><span class="glyphicon glyphicon-open" aria-hidden="true"></span> import</button>').click(function(){
							$fileSelector.click();
							return false;
						});
						
						var $filename = $('<span>').html('no file selected');
						
						var $fileSelector = $('<input type="file" class="form-control">').hide().attr('accept',[].concat(csvExt,jsonExt).map(function(e){return '.'+e;}).join(',')).change(function(){
							var input = $(this)[0],
								file = input.files ? input.files[0] : null,
								dfr = $.Deferred(); // asynchronous reading
							
							// init
							data_ = null;
							loading_ = false;
							$meta.hide().empty();
							$filename.html('no file selected');
							
							if (!input.files) {
								dfr.reject("This browser doesn't seem to support the `files` property of file inputs.");
							}
							else if (!input.files[0]) {
								dfr.reject('Please select a file');
							}
							else {
								loading_ = true;
								
								$filename.text(file.name);
								
								var nameItem = self.form().findItem('name'),
									extension = file.name.indexOf('.')>=0 ? file.name.split('.').pop().toLowerCase() : '',
									format = null,
									fr = new FileReader(),
									content = '';
								
								if(csvExt.indexOf(extension) != -1) format = 'csv';
								if(jsonExt.indexOf(extension) != -1) format = 'json';
								
								if(!format){
									dfr.reject('Not a JSON or CSV file !');
								}
								else {
									if(nameItem && !nameItem.getValue())
										nameItem.setValue(file.name.replace(/\.[^.]*$/i,'.db'));
									
									fr.onload = function(){
										content = fr.result; // as string
										var data;
										
										try{
											// csv or json ?
											if(format=='csv'){
												data = readCSV(content);
											}
											else if(format=='json'){
												data = JSON.parse(content);
											}
											
											if(data){
												if(data.length>0)
													dfr.resolve(data);
												else
													dfr.reject('empty content');
											}
											else
												dfr.reject('invalid data (must be either JSON or CSV content).');
										}
										catch(e){
											dfr.reject(e);
										}
									};
									fr.onerror = fr.onabort = function(){
										dfr.reject('an error occurs while reading the file');
									}
									fr.readAsText(file);
								}
								
							}
							
							dfr
								.done(function(data){
									
									self.setError(null, 'content');
									
									var keys = Object.keys(data[0]);
									
									$meta.append('<dt>Format</dt>','<dd>'+format.toUpperCase()+'</dd>');
									$meta.append('<dt>Size</dt>','<dd>'+data.length+' rows, '+keys.length+' columns ('+EThing.utils.sizeToString(file.size)+')</dd>');
									
									// preview
									var line = 0, i;
									for(i=0; i<content.length; i++){
										if(content.charAt(i)=="\n" && ++line > 5)
											break;
									}
									$meta.append('<dt>Preview</dt>','<dd><pre>'+content.substr(0,i)+'</pre></dd>');
									
									// date field
									var $dateField = $('<select data-name="date-field" class="form-control">'), select = false;
									$dateField.append('<option value="#none#" >none</option>');
									for(i=0; i<keys.length;i++){
										var key = keys[i], sel = false;
										if(key.length){
											if(!select)
												select = sel = (key == 'date' || (typeof data[1][key] == 'string' && data.length>1 && !isNaN(Date.parse(data[1][key])))); // try to auto detect date column
											$dateField.append('<option value="'+encodeURIComponent(key)+'" '+(sel ? 'selected' : '')+'>'+key+'</option>');
										}
									}
									$meta.append('<dt>Date field</dt>',$('<dd>').append($dateField));
									
									
									
									$meta.show(200);
									
									data_ = data;
								})
								.fail(function(errorString){
									self.setError(errorString, 'content');
								})
								.always(function(){
									loading_ = false;
								});
							
							
						});
						var $meta = $('<div class="indent">').hide();
						return $('<div class="ellipsis">').append($btn, ' ', $filename, $meta);
					},
					set: function($input,v){},
					get: function($e){
						if(loading_){
							throw "Please wait ... the file is being processed.";
						}
						
						if(!data_){
							return null;
						}
						
						// date field
						var dateField = $e.find('select[data-name="date-field"]').val();
						if(dateField && dateField != 'date' && dateField != '#none#'){
							dateField = decodeURIComponent(dateField);
							for(var i=0; i<data_.length; i++){
								data_[i].date = data_[i][dateField];
								delete data_[i][dateField];
							}
						}
						
						return data_;
					}
				}
			});
		}
		
		$.FormModal({
			item: new $.Form.FormLayout(formEntries),
			title: '<span class="glyphicon glyphicon-list" aria-hidden="true"></span> Create a new Table',
			validLabel: '+Add'
		},function(props){
			
			if(dir instanceof EThing.Folder && dir.name().length && props.name){
				props.name = dir.name()+'/'+props.name;
			}
			
			var dfr = EThing.Table.create(props).done(function(r){
				// the creation was successful, close the dialog and reload
				if(EThing.arbo.isLoaded())
					EThing.arbo.add(r);
				
				if(typeof callback == 'function')
					callback.call(r);
			});
			
			Uploader.UI.add(props.name,dfr);
		});
		
	}
	
	
	
	
	
	var Uploader = {
		
		upload: function(file, dir, cb){
			
			if(Array.isArray(file)){
				for(var i=0; i<file.length; i++)
					Uploader.upload(file[i],dir,cb);
				return;
			}
			
			if(!file || !file.name)
				return;
			
			var fr = new FileReader();
			
			fr.onload = function(){
				
				// transform the result into base64 string
				var binary = '',
					bytes = new Uint8Array(fr.result);
				for (var i = 0; i < bytes.byteLength; i++) {
					binary += String.fromCharCode( bytes[ i ] );
				}
				
				var b64data = window.btoa(binary),
					name = file.name;
				
				if(dir instanceof EThing.Folder && dir.name().length)
					name = dir.name()+'/'+name;
				
				var dfr = EThing.File.create({
					'name': name,
					'content': b64data
				}).done(function(r){
					// the creation was successful, reload
					EThing.arbo.add(r);
					
					if(typeof cb == 'function')
						cb(r,file);
					
				});
				
				Uploader.UI.add(file.name,dfr);
				
			};
			
			fr.readAsArrayBuffer(file);
			
		},
		
		UI:{
			
			build: function(){
				var $html = $('<div class="uploader">'),
					$header = $('<div class="uploader-header">'),
					$body = $('<div class="uploader-body">');
				
				$header.append(
					'<span class="uploader-header-title"></span>',
					$('<span class="uploader-header-close glyphicon glyphicon-remove" aria-hidden="true"></span>').click(function(){
						Uploader.UI.close();
					}).hide()
				);
				
				$html.append($header,$body).appendTo('body');
				
				return $html;
			},
			close: function(){
				$('body>.uploader').remove();
			},
			update: function(){
				
				var items = 0, done = 0, fail = 0, uploading = 0, title = "";
				$('.uploader-item','.uploader').each(function(){
					var state = $(this).data('state');
					items++;
					switch(state){
						case 'done':
							done++;
							break;
						case 'fail':
							fail++;
							break;
						case 'uploading':
							uploading++;
							break;
					}
				});
				
				if(uploading)
					title = 'Uploading '+uploading+' item'+(uploading>1?'s':'');
				else
					title = items+' upload'+(uploading>1?'s':'')+' complete';
				
				var $ui = $('body>.uploader');
				
				$('.uploader-header-title',$ui).html(title);
				$('.uploader-header-close',$ui).toggle(!uploading);
				
			},
			add: function(name,deferred){
				var $ui = $('body>.uploader');
				if(!$ui.length)
					$ui = Uploader.UI.build();
				
				var $item = $('<div class="uploader-item">'),
					$state = $('<div class="uploader-item-state">'),
					$progress = $('<div class="uploader-item-progress"><div></div></div>'),
					hasProgress = false;
				
				$item.append(
					'<span class="uploader-item-name">'+name+'</span>',
					$state.html('<span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span>')
				).appendTo($ui.children('.uploader-body'));
				
				$item.data('state','uploading');
				
				Uploader.UI.update();
				
				deferred.progress(function(evt){
					if(evt.lengthComputable){
						var ratio = Math.round(evt.loaded / evt.total);
						$('div',$progress).css('width',ratio+'%');
						if(!hasProgress){
							$state.html($progress);
							hasProgress = true;
						}
					}
				});
				
				deferred.done(function(){
					$state.html('<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>');
					$item.data('state','done');
					$item.addClass('uploader-item-done');
				});
				
				deferred.fail(function(){
					$state.html('<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>');
					$item.data('state','fail');
					$item.addClass('uploader-item-fail');
				});
				
				deferred.always(function(){
					Uploader.UI.update();
				});
				
				
			}
			
		}
		
	}
	
	
	
	EThing.ui = $.extend(true,EThing.ui || {}, {
		
		properties: properties,
		createApp: createApp,
		createDevice: createDevice,
		createFile: createFile,
		createTable: createTable,
		settings: settings,
		edit: edit,
		getResourceProperties: getResourceProperties,
		getResourceProperty: getResourceProperty,
		getResourceFormattedValues: getResourceFormattedValues,
		getResourceForm: getResourceForm,
		
		Uploader: Uploader
	});
	
})();