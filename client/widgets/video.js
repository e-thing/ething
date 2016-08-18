(function(){
	
var contentTypesList = [
	"application/javascript",
	"application/json", 
	"application/xml", 
	"image/bmp", 
	"image/gif", 
	"image/jpeg", 
	"image/png", 
	"text/css", 
	"text/html", 
	"text/plain", 
	"text/xml"
];
var headersList = {
	"Accept": contentTypesList,
	"Accept-Charset": null,
	"Accept-Encoding": null,
	"Accept-Language": null,
	"Accept-Datetime": null,
	"Authorization": null,
	"Cache-Control": null,
	"Connection": ["keep-alive","close",""],
	"Cookie": null,
	"Content-Length": null,
	"Content-MD5": null,
	"Content-Type": contentTypesList,
	"Date": null,
	"Expect": null,
	"Forwarded": null,
	"From": null,
	"Host": null,
	"If-Match": null,
	"If-Modified-Since": null,
	"If-None-Match": null,
	"If-Range": null,
	"If-Unmodified-Since": null,
	"Max-Forwards": null,
	"Origin": null,
	"Pragma": null,
	"Proxy-Authorization": null,
	"Range": null,
	"Referer": null,
	"TE": null,
	"Transfer-Encoding": ["chunked", "compress", "deflate", "gzip", "identity"],
	"User-Agent": null,
	"Upgrade": null,
	"Via": null,
	"Warning": null
};
	
var sheet = document.createElement('style')
sheet.innerHTML = ".typeahead {max-height: 200px; overflow-y: auto;}";
document.body.appendChild(sheet);

	

	
	var defaultOptions = {
		
	};
	
	
	var VideoWidget = function(element,opt){
		
		var options = $.extend(true,{
			type: null, // 'url', 'file'
		}, defaultOptions, opt);
		
		var $element = $(element), self = this;
		
		
		var $video = $('<video controls>Your browser does not support the video tag.</video>').css({
			'max-width': '100%',
			'max-height': '100%',
			'display': 'block',
			'margin': 'auto'
		});
		
		$element.html($video);
		
		function setContent(url){
			
			$video.prepend(
				'<source src="'+url+'" type="video/mp4">',
				'<source src="'+url+'" type="video/ogg">'
			);
			
		}
		
		if(options.type == 'url'){
			
			var url = 'proxy?url='+encodeURIComponent(options.url);
			
			if(options.auth){
				var auth = encodeURIComponent(options.auth.type) + ';' + encodeURIComponent(options.auth.user) + ';' + encodeURIComponent(options.auth.password);
				url += '&auth='+encodeURIComponent(auth);
			}
			
			setContent(EThing.toApiUrl(url,true));
			
		}
		else if(options.type == 'file'){
			
			var fileId = options.fileId;
			
			EThing.get(fileId).done(function(file){
				setContent(file.getContentUrl(true));
			});
			
		}
		
	}
	
	
	
	var SwaggerParamTypeToFormStandardItem = function(type){
		var options = {
			input: 'text'
		};
		
		switch(type){
			case 'number':
			case 'integer':
				options.input = 'number';
				break;
			case 'string':
				options.input = 'text';
				break;
			case 'boolean':
				options.input = ['true','false'];
				options.get = function($input){
					return $input.val() == 'true';
				}
				break;
		}
		
		return new $.Form.StandardItem(options);
	}
	
	
	return {
		
		// must return a function which returns an options object
		factory: function(container, preset){
			
			preset = $.extend(true,{}, defaultOptions, preset);
			
			var videoElement = document.createElement('video');
			
			var form = new $.Form(container,
				new $.Form.SelectPanels({
					name: 'source',
					items: [{
						name: 'file',
						item: new $.Form.FormLayout({
							items:[{
								label: 'file',
								name: 'fileId',
								item: new $.Form.ResourceSelect({
									filter: function(r){
										return (r instanceof EThing.File) && (/ogg|mp4/i.test(r.extension()) || !!(videoElement.canPlayType && videoElement.canPlayType(r.mime()).replace(/no/, '')));
									}
								})
							}]
						})
					},{
						name: 'url',
						item: new $.Form.FormLayout({
							name: 'urlForm',
							items:[{
								name: 'url',
								item: {
									input: 'text',
									validator: $.Form.validator.NotEmpty,
									attr:{
										placeholder: 'http://example.com'
									}
								}
							},{
								name: 'auth',
								label: 'authentication',
								item: new $.Form.FormLayout([{
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
								}]),
								checkable: true,
								check: false
							}]
						})
					}]
				})
			);
			
			if(preset)
				form.setValue(preset);
			
			
			
			return function(){
				return form.validate();
			}
		},
		
		instanciate: function(element, options){
			new VideoWidget(element,options);
		}
	};
	
})()