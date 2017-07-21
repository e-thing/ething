(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','ething','js/ui','text!./header.html','css!./header','bootstrap'], factory);
    }
}(this, function ($, EThing, UI, template) {
	
	
	console.log('loading ui/header.js');
	
	var $html = $(template);
	
	$html.find('#nav-api').attr('href', 'http://petstore.swagger.io/?url='+EThing.toApiUrl('swagger.json'));
	
	$('#nav-logout',$html).click(function(){
		EThing.auth.reset();
		window.location.assign('../session/logout');
	});
	
	var update = function(){
		
		var basenameurl = UI.parseUrl().path;
		var hrefRegExp = new RegExp('^#!'+basenameurl+'($|\\?|#)');
		
		$html.find('li:not(.selection-disabled)>a[href]').each(function(){
			var $this = $(this),
				href = $this.attr('href'),
				selected = false;
			
			if(href!='#'){
				selected =  hrefRegExp.test(href);
			}
			
			$this.parent().toggleClass('selected',selected);
		})
	};
	
	var updateDataFolders = function(){
		var $ulFolders = $html.find('[data-role="data-folders"]').empty();
		EThing.arbo.find(function(r){
			return r instanceof EThing.Folder && !r.isRoot;
		}).forEach(function(f){
			$ulFolders.append('<li class="selection-disabled"><a href="#!data?path='+encodeURIComponent(f.id())+'" data-toggle="collapse" data-target="#main-navbar.in"><span class="glyphicon glyphicon-folder-close" aria-hidden="true"></span> '+f.name()+'</a></li>');
		});
		
		var enable = !!$ulFolders.children().length;
		$ulFolders.parent().toggleClass('dropdown-hover',enable);
		if(enable)
			$ulFolders.prepend('<li class="dropdown-header">Folders</li>');
		
	}
	
	EThing.on('ething.arbo.loaded ething.file.created ething.table.created ething.device.created ething.app.created ething.resource.removed', updateDataFolders);
	
	update();
	
	UI.on('ui-pageChange', update);
	
	
	var Header = {
		$element : $html,
		update: update,
		setTitle: function(text, link){
			var $title = $html.find('.navbar-title').html(text).removeAttr('href');
			if(link){
				$title.attr('href', link);
			}
		},
		addAction: function(options){
			var $btn = $(options.html || '<button type="button" class="btn btn-default">');
			
			if(options.icon)
				$btn.append('<span class="glyphicon glyphicon-'+this.icon+'" aria-hidden="true"></span>');
			if(options.label)
				$btn.append(' '+options.label);
			if(options.click)
				$btn.click(options.click);
			
			$btn.addClass('navbar-collapse-btn').appendTo(  $html.find('.navbar-extra-btn') );
		},
		setActions: function(actions){
			$html.find('.navbar-extra-btn').empty();
			if($.isPlainObject(actions)) actions = [actions];
			if(Array.isArray(actions))
				actions.forEach(function(action){
					this.addAction(action);
				}, this);
		}
	};
	
	UI.Header = Header;
	
	UI.$element.prepend(Header.$element);
	
	UI.on('ui-pageChange', function(){
		Header.setTitle('e-Thing','#');
		Header.setActions(null);
	});
	
	return Header;
}));