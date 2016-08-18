(function () {
	
	var $html = $(
	
	'<nav id="navbar" class="navbar navbar-default navbar-fixed-top">'+
	  '<div class="container">'+
		'<div class="navbar-header">'+
		  
		  '<button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#main-navbar" aria-expanded="false" aria-controls="navbar">'+
			'<span class="sr-only">Toggle navigation</span>'+
			'<span class="icon-bar"></span>'+
			'<span class="icon-bar"></span>'+
			'<span class="icon-bar"></span>'+
		  '</button>'+
		  '<div class="visible-xs-block" data-role="navbar-extra-btn"></div>'+
		  '<a class="navbar-brand hidden-xs" href="dashboard.html">e-Thing</a>'+
		  '<div class="navbar-path visible-xs-block"></div>'+
		'</div>'+
		'<div class="navbar-collapse collapse" id="main-navbar">'+
		  '<ul class="nav navbar-nav">'+
			'<li><a href="dashboard.html" data-toggle="collapse" data-target="#main-navbar.in"><span class="glyphicon glyphicon-dashboard" aria-hidden="true"></span> Dashboard</a></li>'+
			'<li><a href="explore.html#!browser" data-toggle="collapse" data-target="#main-navbar.in"><span class="glyphicon glyphicon-search" aria-hidden="true"></span> Explore</a></li>'+
			'<li><a href="explore.html#!device" data-toggle="collapse" data-target="#main-navbar.in"><span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Devices</a></li>'+
			'<li><a href="explore.html#!app" data-toggle="collapse" data-target="#main-navbar.in"><span class="glyphicon glyphicon-flash" aria-hidden="true"></span> Apps</a></li>'+
			'<li><a href="explore.html#!map" data-toggle="collapse" data-target="#main-navbar.in"><span class="glyphicon glyphicon-map-marker" aria-hidden="true"></span> Map</a></li>'+
			'<li><a href="https://e-thing.github.io/doc" target="_blank" data-toggle="collapse" data-target="#main-navbar.in"><span class="glyphicon glyphicon-book" aria-hidden="true"></span> Doc</a></li>'+
		  '</ul>'+
		  
		  '<ul class="nav navbar-nav navbar-right">'+
			'<li class="dropdown">'+
			  '<a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false"><span class="glyphicon glyphicon-user" aria-hidden="true"></span> <span id="nav-user-name" class="visible-xs-inline visible-md-inline visible-lg-inline"></span> <span class="caret"></span></a>'+
			  '<ul class="dropdown-menu">'+
				'<li><a href="profile.html" data-toggle="collapse" data-target="#main-navbar.in"><span class="glyphicon glyphicon-user" aria-hidden="true"></span> Profile</a></li>'+
				'<li><a href="developer.html" data-toggle="collapse" data-target="#main-navbar.in"><span class="glyphicon glyphicon-console" aria-hidden="true"></span> Developer</a></li>'+
				'<li role="separator" class="divider"></li>'+
				'<li><a href="../admin" data-toggle="collapse" data-target="#main-navbar.in"><span class="glyphicon glyphicon-wrench" aria-hidden="true"></span> Admin panel</a></li>'+
				'<li role="separator" class="divider"></li>'+
				'<li><a href="#" id="nav-logout" data-toggle="collapse" data-target="#main-navbar.in"><span class="glyphicon glyphicon-log-out" aria-hidden="true"></span> Logout</a></li>'+
			  '</ul>'+
			'</li>'+
		  '</ul>'+
		'</div>'+
	  '</div>'+
	'</nav>'
	
	);
	
	
	if(EThing.auth.isAuthenticated())
		$('#nav-user-name',$html).text(EThing.auth.getUser().name());
	
	$('#nav-logout',$html).click(function(){
		EThing.auth.logout();
		$(window).off('hashchange');
		window.location.replace('signin.html');
	});
	
	$(function(){
		$('body').prepend($html);
	});
	
	
	
	
	Header = {
		
		brand: $html.find('.navbar-brand').text(),
		
		homeUrl: $html.find('.navbar-brand').attr('href'),
		
		// whatever
		setMobileCustomTitle: function(content){
			var $h = $html.find('.navbar-path').empty(), self = this;
			if(content)
				$h.append(content);
			else
				$h.append(
					$('<span class="home">').html(self.brand).click(function(){
						if(self.homeUrl) window.location.assign(self.homeUrl);
					})
				);
		},
		
		// brand > title
		setMobileTitle: function(title){
			var self = this;
			Header.setMobileCustomTitle([
				$('<span class="home">').html(self.brand).click(function(){
					if(self.homeUrl) window.location.assign(self.homeUrl);
				}),
				'<span class="name category" >'+title+'</span>'
			]);
		},
		
		// <- title
		setMobilePath: function(basename, back){
			if(typeof back != 'function')
				back = function(){
					window.history.back();
				}
			Header.setMobileCustomTitle([
				$('<span class="glyphicon glyphicon-arrow-left prev" aria-hidden="true"></span>').click(back),
				'<span class="name">'+basename+'</span>'
			]);
		},
		
		// brand
		restoreMobileTitle: function(){
			Header.setMobileCustomTitle();
		}
		
		
	};
	
	
	var update = function(){
		var url = window.location.href,
			basenameurl = url.replace(/^[^#]*\//,''),
			re_sel = new RegExp('^'+basenameurl);
		
		$html.find('li>a[href]').each(function(){
			var $this = $(this),
				href = $this.attr('href'),
				selected = false;
			
			if(href!='#'){
				selected =  basenameurl.indexOf(href) === 0;
			}
			
			$this.parent().toggleClass('selected',selected);
		})
	};
	
	update();
	
	$(window).on('hashchange', update);
		
	
	
	
})()