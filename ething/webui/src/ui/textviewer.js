(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define([
			'require', 
			'jquery',
			'ething',
			'codemirror',
			
			// autoformating
			'js-beautify/beautify',
			'js-beautify/beautify-html',
			'js-beautify/beautify-css',
			
			"css!codemirror",
			"codemirror/addon/display/autorefresh",
			"codemirror/addon/display/fullscreen",
			"css!codemirror/addon/display/fullscreen",
			
			// search addon, see https://codemirror.net/demo/search.html
			"css!codemirror/addon/search/matchesonscrollbar",
			"css!codemirror/addon/dialog/dialog",
			"codemirror/addon/dialog/dialog",
			"codemirror/addon/search/search",
			"codemirror/addon/search/searchcursor",
			"codemirror/addon/scroll/annotatescrollbar",
			"codemirror/addon/search/matchesonscrollbar",
			"codemirror/addon/search/jump-to-line",
			
			// modes autoloader
			"codemirror/mode/meta",
			
			'ui/opendialog',
			'ui/savedialog',
			'css!ui/textviewer'
		], factory);
    }
}(this, function (require, $, EThing, CodeMirror, b0, b1, b2) {

var js_beautify = b0.js_beautify;
var html_beautify = b1.html_beautify;
var css_beautify = b2.css_beautify;

// autoload modes
CodeMirror.autoLoadMode = function(instance, mode) {
	if (!CodeMirror.modes.hasOwnProperty(mode)){
		var src = "codemirror/mode/"+mode+"/"+mode;
		require([src], function(){
			instance.setOption("mode", instance.getOption("mode"));
		});
	}
};


CodeMirror.modeInfo.sort(function(a,b){
	return a.name.localeCompare(b.name);
});
	
	
var filter = function(r){
	// File => open everything except image, audio or video
	return ((r instanceof EThing.File) && !/^(image|audio|video)\//.test(r.mime())) || (r instanceof EThing.App);
}

var isTouchDevice = navigator ? (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase())) : false;




var re_autoformat = /html|json|javascript|css/i;

var defaultOptions = {
	readonly: false, // if set, readonly mode, no change can be made, no save available
	data: null, // can either be a string to be shown or a deferred object (AJAX request ...) or a resource
	mode: null, // for syntax coloration ..., default to 'text/plain'
	filename: null, // the name of the current content, null if none
	lint: false, // activate the lint add-on for some compatible languages
	toolbar: {
		enable: true,
		filename: {
			enable: true,
			format: '%f' // format string (%f: filename) or function
		}
	}
};

var defaultActions = {
	'open': {
		icon: 'glyphicon-folder-open',
		on: function(tv){
			// returns a deferred object
			return $.OpenDialog({
				filter: filter,
				limit: 1
			}).then(function(r){
				return tv.open(r[0]); // piped deferred
			});
		}
	},
	'save':{
		icon: 'glyphicon-floppy-disk',
		before:function(tv){
			if(!tv.resource){
				tv.triggerAction('saveas');
				return false;
			}
			if(tv.hasLintError()){
				if(!confirm('Do you really want to save with some errors ?'))
					return false;
			}
			tv.__saveNotifUid = tv.notify('Saving ...');
		},
		on: function(tv){
			var text = tv.text(), d = tv.resource.write(text);
			return d.fail(function(e){
				tv.notify(e.message);
			});
		},
		after:function(tv,deferred){
			deferred
				.always(function(){
					if(tv.__saveNotifUid){
						tv.removeNotification(tv.__saveNotifUid);
						delete tv.__saveNotifUid;
					}
				})
				.then(
					function(){
						// save successfull
						tv.markClean(); // Set the editor content as 'clean', a flag that it will retain until it is edited, and which will be set again when such an edit is undone again
					},
					function(){
						// on fail do nothing, do not mark the content as clean
					}
				);
		},
		showOnReadOnly: false
	},
	'saveas':{
		icon: 'glyphicon-floppy-save',
		on:function(tv){
			// SaveDialog returns a deferred object
			return $.SaveDialog({
				title: 'Save as ...',
				filter: filter,
				preset: tv.resource || null,
				createPreset:{
					name: tv.getFilename()
				}
			}).then(function(r){
				// must return a deferred object when the saving is asynchrone
				tv.resource = r;
				return tv.triggerAction('save').done(function(){
					tv.open(r);
				});
			});
		},
		showOnReadOnly: false
	},
	'undo':{
		icon:'glyphicon-arrow-left',
		before:function(tv){
			tv.editor().undo();
		},
		showOnReadOnly: false
	},
	'redo':{
		icon:'glyphicon-arrow-right',
		before:function(tv){
			tv.editor().redo();
		},
		showOnReadOnly: false
	},
	'autoformat':{
		icon:'glyphicon-indent-left',
		on:function(tv){
			var cm = tv.editor(),
				text = tv.text(),
				mode = cm.getOption("mode"), // cm.getMode().name
				fn = /css/i.test(mode) ? css_beautify : (/(javascript|json)/i.test(mode) ? js_beautify : html_beautify),
				sweetText = fn(text,{
					indent_size: cm.getOption('indentUnit'),
					indent_inner_html: true, // indent <head> and <body> sections
					wrap_line_length: 0 // disable wrap
				});
			if(text!=sweetText)
				cm.setValue(sweetText);
		},
		showOnReadOnly: false
	},
	'mode':{
		enable: false,
		tooltip: false,
		html: '<div class="btn-group btn-group-sm tv-mode" role="group"><button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"></button><ul class="dropdown-menu dropdown-menu-right"></ul></div>'
	},
	'fullscreen':{
		enable: true,
		icon:'glyphicon-resize-full',
		on: function(tv){
			var cm = tv.editor(),
				isFullscreen = cm.getOption("fullScreen");
			
			cm.setOption("fullScreen", !isFullscreen)
			
			$('.tv-action[data-role="fullscreen"] .glyphicon',tv.$element).removeClass(isFullscreen ? 'glyphicon-resize-full' : 'glyphicon-resize-small').addClass(isFullscreen ? 'glyphicon-resize-small' : 'glyphicon-resize-full');
		}
	}
};




var TextViewer = function(element,options, onready) {
	
	var self = this;
	
	this.$element = $(element);
	this.options = $.extend(true,{actions: $.extend(true, {}, defaultActions)},defaultOptions,options);
	
	// events layer
	['on','off','one','trigger'].forEach(function(method){
		self[method] = function(){
			var args = Array.prototype.slice.call(arguments);
			self.$element[method].apply(self.$element,args);
		}
	});
	
	this.$element.empty().removeClass('tv-readonly tv-toolbar').addClass('TextViewer');
	
	/*
	 build the toolbar
	*/
	
	// build the toolbar
	var $tb = $('<div class="tv-toolbar"><div class="btn-group btn-group-sm tv-actions"></div><div class="tv-filename"></div></div>')
		.hide()
		.appendTo(this.$element);
	
	$.each(this.options.actions,function(name,action){
		self.addAction(name,action);
	});
	
	if(!this.options.actions.mode.enable){
		$tb.append('<div class="tv-mode dropdown"><span data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"></span><ul class="dropdown-menu dropdown-menu-right"></ul></div>');
	}
	
	
	
	
	/*
	* init Codemirror instance
	*/
	
	var $content = $('<div>').addClass('tv-content').appendTo(this.$element).html('loading...');
	
	
	// fill the mode dropdown list with the available modes :
	var $ulmode = $('.tv-mode>ul',this.$element);
	for(var i = 0; i<CodeMirror.modeInfo.length; i++)
		$ulmode.append('<li><a>'+CodeMirror.modeInfo[i].name+'</a></li>');
	$ulmode.find('li > a').click(function(){
		var modeName = $(this).text();
		self.setMode(CodeMirror.findModeByName(modeName));
	});
	
	$content.empty();
	
	this._editor = new CodeMirror($content[0], {
		"lineNumbers": true,
		"lineWrapping": false,
		'mode': 'text/plain',
		'viewportMargin':Infinity,
		'extraKeys': {
			"Ctrl-S": function(cm) {
				self.triggerAction('save');
			},
			"F11": function(cm) {
				self.triggerAction('fullscreen');
			},
			"Esc": function(cm) {
				self.triggerAction('fullscreen');
			}
		},
		
	});
	
	this._editor.setSize(null,'auto');
	this._editor.off();
	this._editor.refresh();
	
	
	var $undo = $('.tv-action[data-role="undo"]',this.$element),
		$redo = $('.tv-action[data-role="redo"]',this.$element);
	
	this._editor.on('change',function(instance,changeObj){
		// The changeObj is a {from, to, text, removed, origin} object containing information about the changes that occurred
		self._updateDirtyState();
		
		$undo.prop( "disabled", instance.historySize().undo==0 );
		$redo.prop( "disabled", instance.historySize().redo==0 );
	});
	
	setTimeout(function(){
		self.trigger('editor-loaded.tv');
	},1);
	
	
	
	/*
	* Open the data
	*/
	this.open(options).always(onready);
	
	

};
TextViewer.prototype.open = function(options){
	var self = this, deferred = $.Deferred(), data = '', error = null;
	
	if(!$.isPlainObject(options))
		options = {
			data: options
		};
	
	$.extend(true,this.options,{
		data: null,
		mode: null,
		filename: null
	},options);
	
	// data as resource
	delete this.resource;
	if(this.options.data instanceof EThing.Resource){
		var resource = this.resource = this.options.data, mime;
		
		// specificities
		if(resource instanceof EThing.File){
			if(!this.options.mode)
				this.options.mode = resource.mime();
			data = resource.read();
		}
		else if(resource instanceof EThing.App){
			this.options.mode = 'text/html'; // override
			data = resource.read();
		}
		else {
			error = new Error('Invalid data !');
		}
		
		this.options.filename = resource.name();
		
	}
	else if(this.options.data instanceof Blob){
		
		if(!this.options.filename && this.options.data.name)
			this.options.filename = this.options.data.name;
		
		this.options.mode = this.options.data.type || 'text/plain';
		
		if(FileReader){
			var fr = new FileReader()
				dfr = $.Deferred();
			fr.onload = function(){
				dfr.resolve(fr.result);
			};
			fr.onerror = fr.onabort = function(){
				dfr.reject();
			}
			fr.readAsText(this.options.data);
			
			data = dfr.promise();
		}
		else {
			error = new Error('No support for FileReader');
		}
	}
	else if(this.options.data !== null)
		data = this.options.data;
	
	// update toolbar
	$('.tv-toolbar',this.$element).toggle(this.options.toolbar.enable);
	$.each(this.options.actions,function(name,action){
		var $action = $('.tv-action[data-role="'+name+'"]',self.$element);
		if($action.length)
			$action.toggle(action.enable && (!self.options.readonly || action.showOnReadOnly));
		else
			self.addAction(name,action);
	});
	
	// set filename
	$('.tv-filename',this.$element)
		.html(this.options.toolbar.filename.enable ? (typeof this.options.toolbar.filename.format == 'function' ? this.options.toolbar.filename.format.call(this,this.getFilename()) : this.options.toolbar.filename.format.replace('%f', this.getFilename())) : '');
	
	
	this.$element.toggleClass('tv-readonly',self.options.readonly);
	this.$element.toggleClass('tv-toolbar',self.options.toolbar.enable);
	
	var nuid = this.notify(this.options.filename ? ('Opening '+this.getFilename()) : 'Opening ...');
	
	var lint;
	if(this.options.lint && !self.options.readonly){
		if(/json/i.test(this.options.mode || ''))
			lint = 'js';
	}
	
	// load some extra addon if necessary
	var addondfr = null;
	if(lint){
		addondfr = $.Deferred();
		var deps = [
			"css!codemirror/addon/lint/lint.min",
			"codemirror/addon/lint/lint.min"
		];
		if(lint=='js'){
			deps.push("https://cdn.rawgit.com/zaach/jsonlint/79b553fb65c192add9066da64043458981b3972b/lib/jsonlint.js");
			deps.push("codemirror/addon/lint/json-lint.min");
		}
		require(deps, function(){
			addondfr.resolve();
		});
	}
	
	// load the data
	this.initialContent = (typeof data == 'string') ? data : '';
	var d = $.when(data, addondfr);
	
	d.always(function(){
		delete self.initialContent;
		
		if(d.state() == 'rejected' && !error)
			error = new Error('unable to load the data !');
			
		var text = typeof arguments[0] == 'string' ? arguments[0] : arguments[0][0];
		
		if(typeof text != 'string' && !error){
			error = new Error('invalid data !');
		}
		
		self.setMode(self.options.mode || self.getFilename());
		
		self.editor().setOption('readOnly',self.options.readonly ? true : false);
		self.editor().setOption('gutters',lint ? ["CodeMirror-lint-markers"] : []);
		self.editor().setOption('lint',lint);
		
		self.editor().setValue(error ? '' : text);
		
		self.markClean();
		self.clearHistory();
		
		console.log('mode: ',self.editor().getOption('mode'));
		
		self.removeNotification(nuid);
		
		if(error){
			self.notify(error);
			deferred.rejectWith(self,[error]);
		}
		else
			deferred.resolveWith(self,[text]);
		
		setTimeout(function(){
			self.trigger('data-loaded.tv');
		},1);
		
	});
	
	return deferred.promise();
	
}
TextViewer.prototype.addAction = function(name,props){
	
	var self = this;
	
	props = $.extend(true,{
		name: name,
		enable: true,
		icon: null,
		showOnReadOnly: true,
		tooltip: null,
		html: function(tv){
			var $html = $('<button type="button" class="btn btn-default">'), name = this.name;
			if(this.icon){
				if(typeof this.icon == 'string' && /^glyphicon-/.test(this.icon))
					$html.prepend('<span class="glyphicon '+this.icon+'" aria-hidden="true">');
				else
					$html.prepend(this.icon);
			}
			else
				$html.prepend(name);
			
			$html.click(function(){
				tv.triggerAction(name);
			});
			
			return $html;
		},
		on: null,
		before: null,
		after: null
	},props);
	
	if(props.tooltip===null)
		props.tooltip = name;
	
	var $action = $(typeof props.html == 'function' ? props.html.call(props,self) : props.html);
	
	$action.attr('data-role',name).addClass('tv-action');
	
	if(!isTouchDevice){
		if(props.tooltip!==false)
			$action.tooltip({
				container: this.$element,
				trigger:'hover',
				placement: 'bottom',
				title: props.tooltip
			});
	}
	
	$action.toggle(props.enable && (!this.options.readonly || props.showOnReadOnly));
	
	this.options.actions[name] = props;
	
	$('.tv-actions',this.$element).append($action);
}
TextViewer.prototype.setMode = function(info){
	var self = this;
	
	if(typeof info == 'string'){
		var value = info;
		if (m = /.+\.([^.]+)$/.exec(value)) { // filename
			info = CodeMirror.findModeByExtension(m[1]);
		} else if (/\//.test(value)) { // mime
			info = CodeMirror.findModeByMIME(value);
		} else { // name
			info = CodeMirror.findModeByName(value);
		}
	}
	
	if(!info)
		info = CodeMirror.findModeByMIME('text/plain');
	
	if($.isPlainObject(info)){
		this.editor().setOption('theme',info.mode + ' default');
		this.editor().setOption('mode',info.mime);
		CodeMirror.autoLoadMode(this.editor(), info.mode);
		
		var action = this.options.actions['autoformat'];
		if(action && action.enable)
			$('.tv-action[data-role="'+action.name+'"]',this.$element).prop( "disabled",!re_autoformat.test(info.mode));
		
		$('.tv-mode>span,.tv-mode>button',this.$element).html(info.name);
	}
}
TextViewer.prototype.markClean = function(){
	if(this.editor()){
		this.editor().markClean();
		this._updateDirtyState();
	}
}
TextViewer.prototype.clearHistory = function(){
	if(this.editor()){
		this.editor().clearHistory();
	}
	$('.tv-action[data-role="undo"]',this.$element).prop( "disabled",true);
	$('.tv-action[data-role="redo"]',this.$element).prop( "disabled",true);
}

TextViewer.prototype.hasLintError = function(){
	var editor = this.editor(), lint;
	if(editor && (lint = editor.getHelper(CodeMirror.Pos(0, 0), "lint"))){
		var state = editor.state.lint;
		if(state.marked.length)
			return true;
	}
	return false;
}
TextViewer.prototype.notify = function(message, timeout){
	if(typeof message != 'string')
		message = message.message || null;
	if(!message || message ==="") return;
	
	var self = this;
	
	var $notify = this.$element.find('.tv-notification');
	if(!$notify.length){
		$notify = $('<div class="tv-notification">').appendTo(this.$element);
	}
	
	// build the message
	var uid = "message-"+String(Math.round(Math.random()*1000000)),
		$message = $('<div id="'+uid+'" class="alert alert-info alert-dismissible" role="alert">').append('<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>',message.message || message);
	
	$message.appendTo($notify);
	
	$notify.show();
	
	if((typeof timeout == 'number') && timeout>0)
		window.setTimeout(function(){
			self.removeNotification(uid);
		},timeout);
	
	return uid;
}
TextViewer.prototype.removeNotification = function(uid){
	var $notify = this.$element.find('.tv-notification');
	if($notify.length){
		$notify.find('#'+uid).remove();
		if(!$notify.find('[id^="message-"]').length){
			$notify.hide();
		}
	}
}
TextViewer.prototype.editor = function(){
	return this._editor || null;
}
TextViewer.prototype.isClean = function(){
	return !!this._isClean;
}
TextViewer.prototype.value = function(value) {
	// No value passed, act as a getter.
	if ( value === undefined ) {
		return this.text();
		
	// Value passed, act as a setter.
	} else { 
		return this.open(value);
	}
}
TextViewer.prototype.text = function(content) {
	return typeof content == 'undefined' ? (this.editor() ? this.editor().getValue() : (this.initialContent)) : this.open(content);
};
TextViewer.prototype.getFilename = function() {
	return this.options.filename || 'untitled';
};
TextViewer.prototype.triggerAction = function(actionName, data) {
	var deferred = $.Deferred(),
		self = this;
	
	var parts = actionName.split('.');
	actionName = parts.shift();
	var subaction = parts.length>0 ? parts.join('.') : null;
	
	if(this.options.actions.hasOwnProperty(actionName) && this.options.actions[actionName].enable){
		var action = this.options.actions[actionName];
		
		var e = $.Event( 'before-trigger-'+actionName+'.tv', { action: actionName } );
		this.trigger(e);
		
		if(e.isDefaultPrevented())
			deferred.rejectWith(self);
		
		if(deferred.state() != "rejected" && $.isFunction(action.before))
			if(action.before.call(action,self,data,subaction) === false){
				deferred.rejectWith(self);
			}
		if(deferred.state() != "rejected"){
			if($.isFunction(action.on)){
				// this handler may return a jQuery deferred object
				try {
					var def = action.on.call(action,self,data,subaction);
					if(def===false)
						deferred.rejectWith(self);
					else
						$.when(def).then(function(result){
							deferred.resolveWith(self,[result]);
						},function(){
							deferred.rejectWith(self);
						});
				}
				catch(e){
					console.log(e);
					self.notify(e);
					deferred.rejectWith(self);
				}
			}
			else{
				deferred.resolveWith(self);
			}
			
			if($.isFunction(action.after))
				action.after.call(action,self,deferred,data,subaction);
		}
	}
	else
		deferred.rejectWith(self);
	
	deferred.done(function(){
		self.trigger('trigger-'+actionName+'.tv');
	});
	
	return deferred.promise();
};
TextViewer.prototype.toggleAction = function(actionName, state) {
	var action = this.options.actions[actionName];
	if(action){
		action.enable = !!state;
		$('.tv-action[data-role="'+action.name+'"]',this.$element).toggle(action.enable);
	}
};


TextViewer.prototype._updateDirtyState = function(){
	var editor = this.editor();
	if(editor){
		var currentCleanState = editor.isClean();
		if(currentCleanState != this._isClean){
			this._isClean = currentCleanState;
			
			// update some internal things
			$('.tv-filename',this.$element).toggleClass('tv-dirty', !currentCleanState);
			$('.tv-action[data-role="save"]',this.$element).prop( "disabled", currentCleanState );
			
			this.trigger('clean-state-change.tv');
		}
	}
}

TextViewer.accept = filter;




/* register as a plugin in jQuery */
	
$.TextViewer = TextViewer;

$.fn.textViewer = function(){
	var args = [].slice.call(arguments);
	
	if (this[0]) { // this[0] is the renderTo div
		
		var instance = $(this[0]).data('textViewer');
		
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
		instance = new TextViewer(this[0],args[0],args[1],args[2],args[3],args[4],args[5],args[6]);
		$(this[0]).data('textViewer',instance);
		
		return this;
	}
};


return TextViewer;

}));