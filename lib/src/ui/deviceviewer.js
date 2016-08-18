(function(){

// necessary to work with ba-bbq
jQuery.browser = jQuery.browser || {};
(function () {
	jQuery.browser.msie = jQuery.browser.msie || false;
	jQuery.browser.version = jQuery.browser.version || 0;
	if (navigator.userAgent.match(/MSIE ([0-9]+)\./)) {
		jQuery.browser.msie = true;
		jQuery.browser.version = RegExp.$1;
	}
})();



var dependency = $.Dependency({
	base: '//cdn.rawgit.com/swagger-api/swagger-ui/v2.2.0/dist',
	url:[
		/*'css/reset.css',*/
		/* 'css/screen.css', */
		'lib/jquery.slideto.min.js',
		'lib/jquery.wiggle.min.js',
		'lib/jquery.ba-bbq.min.js',
		'lib/handlebars-4.0.5.js',
		'lib/js-yaml.min.js',
		'lib/lodash.min.js',
		{
			url: 'lib/highlight.9.1.0.pack.js',
			then: 'lib/highlight.9.1.0.pack_extended.js'
		},
		'lib/jsoneditor.min.js',
		'lib/marked.js'
	],
	then:{
		url:[
			'lib/backbone-min.js',
		],
		then: [
			'swagger-ui.min.js',
			'lib/swagger-oauth.js'
		]
	}
},function(){
	// some defaults :
	
	hljs.configure({
		highlightSizeThreshold: 5000
	});
	
	JSONEditor.defaults.options.theme = 'bootstrap3';
});


	
	
	




/**
* Simplify the swagger ui view
*/
function customize(instance){
	
	var $element = instance.$element,
		device = instance.getDevice();
	
	$('#swagger-ui-container > .info', $element).addClass('container');
	
	$('#swagger-ui-container > .info > .info_title', $element).append(
		'<a target="_blank" href="explore.html#!device:'+device.id()+'">[device: '+device.name()+']</a>'
	);
	
	
	
	$('tbody.operation-params>tr',$element).each(function(){
		var $tr = $(this), $tds = $tr.children('td');
		
		var name = $tds.eq(0).text(),
			description = $tds.eq(2).text(),
			$input = $tds.eq(1),
			required = $tds.eq(0).hasClass('required');
		
		if(required)
			$tr.addClass('required');
		
		$input.addClass('keep');
		
		$tr.prepend(
			'<td class="keep" data-type="name">'+name+'</td>',
			'<td class="keep markdown" data-type="description">'+description+'</td>'
		);
		
	});
	
	$('.operation>.content>form>table>tbody',$element).each(function(){
		
		var $tbody = $(this), classnames = $(this).attr('class');
		
		var $table = $tbody.closest('table'), $prev = $table.prev();
		if(!/(^| )operation-params($| )/i.test(classnames)){
			// hide
			$table.hide();
		}
		// also hide the title section
		if($prev.is('h1,h2,h3,h4,h5,h6'))
			$prev.hide();
		
	});
	
	$('.operation>.content>h4:contains("Implementation Notes")',$element).hide();
	
	$('.operation-params .parameter-content-type',$element).prev().filter('br').remove();
	
	$('input:not([type="submit"]):not([type="button"]), select, textarea',$element).filter(':not(.form-control)').addClass('form-control');
	
	$('button, input[type="button"], input[type="submit"]',$element).filter(':not(.btn)').addClass('btn btn-default');
	
	$('.response_throbber',$element).text('loading...');
}




function DeviceViewer(element,opt){
	
	var self = this;
	
	if(opt instanceof EThing.Device)
		opt = {
			device: opt
		};
	
	$.AbstractPlugin.call(this,element,opt);
	
	
	this.$element.addClass('swagger-section').html('<div class="loader">loading...</div>');
	
	$.when(
		this.getDevice().getDescriptor(),
		dependency.require()
	).done(function(){
		
		var spec = arguments[0][0];
		
		
		if(window.swaggerUi) delete window.swaggerUi;
		
		
		self.$element.empty().addClass('swagger-section').append(
			'<div id="message-bar" class="swagger-ui-wrap">&nbsp;</div>'+
			'<div id="swagger-ui-container" class="swagger-ui-wrap"></div>'
		);
		
		window.swaggerUi = new SwaggerUi({
			spec: spec,
			client: EThing.utils.ethingHTTPSwaggerClient,
			dom_id: "swagger-ui-container",
			supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
			validatorUrl: null, // disable validation
			onComplete: function(swaggerApi, swaggerUi){
				customize(self);
			},
			onFailure: function(data) {
				console.log("Unable to Load SwaggerUI");
			},
			docExpansion: "list",
			jsonEditor: true,
			defaultModelRendering: 'schema',
			showRequestHeaders: false
		});
		
		window.swaggerUi.load();
		
	});
	
}

DeviceViewer.prototype.getDevice = function(){
	return this.options.device;
}


/* register as a plugin in jQuery */
if (window.jQuery)
	window.jQuery.addPlugin('DeviceViewer',DeviceViewer);


	
dependency.done(function(){
	
	
	/**
	* Override this method to show an image from a blob content, compatible with ethingHTTPSwaggerClient.
	* Else it will load the image twice !
	*/
	SwaggerUi.Views.OperationView.prototype.showStatus = function(response) {
		var url, content;
		if (response.content === undefined) {
		  content = response.data;
		  url = response.url;
		} else {
		  content = response.content.data;
		  url = response.request.url;
		}
		var headers = response.headers;
		content = jQuery.trim(content);

		// if server is nice, and sends content-type back, we can use it
		var contentType = null;
		if (headers) {
		  contentType = headers['Content-Type'] || headers['content-type'];
		  if (contentType) {
			contentType = contentType.split(';')[0].trim();
		  }
		}
		$('.response_body', $(this.el)).removeClass('json');
		$('.response_body', $(this.el)).removeClass('xml');

		var supportsAudioPlayback = function(contentType){
		  var audioElement = document.createElement('audio');
		  return !!(audioElement.canPlayType && audioElement.canPlayType(contentType).replace(/no/, ''));
		};
		
		var supportsVideoPlayback = function(contentType){
		  var videoElement = document.createElement('video');
		  return !!(videoElement.canPlayType && videoElement.canPlayType(contentType).replace(/no/, ''));
		};

		var pre;
		var code;
		if (!content) {
		  code = $('<code />').text('no content');
		  pre = $('<pre class="json" />').append(code);

		  // JSON
		} else if (contentType === 'application/json' || /\+json$/.test(contentType)) {
		  var json = null;
		  try {
			json = JSON.stringify(JSON.parse(content), null, '  ');
		  } catch (_error) {
			json = 'can\'t parse JSON.  Raw result:\n\n' + content;
		  }
		  code = $('<code />').text(json);
		  pre = $('<pre class="json" />').append(code);

		  // XML
		} else if (contentType === 'application/xml' || /\+xml$/.test(contentType)) {
		  code = $('<code />').text(this.formatXml(content));
		  pre = $('<pre class="xml" />').append(code);

		  // HTML
		} else if (contentType === 'text/html') {
		  code = $('<code />').html(_.escape(content));
		  pre = $('<pre class="xml" />').append(code);

		  // Plain Text
		} else if (/text\/plain/.test(contentType)) {
		  code = $('<code />').text(content);
		  pre = $('<pre class="plain" />').append(code);


		  // Image
		} else if (/^image\//.test(contentType)) {
			
			if(response.data instanceof Blob){
				// build an image from the blob data
				var urlCreator = window.URL || window.webkitURL;
				var imageUrl = urlCreator.createObjectURL( response.data );
				
				var image = new Image();
				image.src = imageUrl;
				pre = image;
			}
			else {
				pre = $('<img>').attr('src', EThing.toApiUrl(url,true)); // include the access token as a query parameter
			}

		  // Audio
		} else if (/^audio\//.test(contentType) && supportsAudioPlayback(contentType)) {
		  pre = $('<audio controls>').append($('<source>').attr('src', EThing.toApiUrl(url,true)).attr('type', contentType));

		  // video
		} else if (/^video\//.test(contentType) && supportsVideoPlayback(contentType)) {
		  pre = $('<video controls>').append($('<source>').attr('src', EThing.toApiUrl(url,true)).attr('type', contentType));

		  // Download
		} else if (headers['Content-Disposition'] && (/attachment/).test(headers['Content-Disposition']) ||
			headers['content-disposition'] && (/attachment/).test(headers['content-disposition']) ||
			headers['Content-Description'] && (/File Transfer/).test(headers['Content-Description']) ||
			headers['content-description'] && (/File Transfer/).test(headers['content-description'])) {

		  if ('Blob' in window) {
			var type = contentType || 'text/html';
			var blob = new Blob([content], {type: type});
			var a = document.createElement('a');
			var href = window.URL.createObjectURL(blob);
			var fileName = response.url.substr(response.url.lastIndexOf('/') + 1);
			var download = [type, fileName, href].join(':');

			// Use filename from response header
			var disposition = headers['content-disposition'] || headers['Content-Disposition'];
			if(typeof disposition !== 'undefined') {
			  var responseFilename = /filename=([^;]*);?/.exec(disposition);
			  if(responseFilename !== null && responseFilename.length > 1) {
				download = responseFilename[1];
			  }
			}

			a.setAttribute('href', href);
			a.setAttribute('download', download);
			a.innerText = 'Download ' + fileName;

			pre = $('<div/>').append(a);
		  } else {
			pre = $('<pre class="json" />').append('Download headers detected but your browser does not support downloading binary via XHR (Blob).');
		  }

		  // Location header based redirect download
		} else if(headers.location || headers.Location) {
		  window.location = EThing.toApiUrl(response.url,true);

		  // Anything else (CORS)
		} else {
		  code = $('<code />').text(content);
		  pre = $('<pre class="json" />').append(code);
		}
		var response_body = pre;
		$('.request_url', $(this.el)).html('<pre></pre>');
		$('.request_url pre', $(this.el)).text(url);
		$('.response_code', $(this.el)).html('<pre>' + response.status + '</pre>');
		$('.response_body', $(this.el)).html(response_body);
		$('.response_headers', $(this.el)).html('<pre>' + _.escape(JSON.stringify(response.headers, null, '  ')).replace(/\n/g, '<br>') + '</pre>');
		$('.response', $(this.el)).slideDown();
		$('.response_hider', $(this.el)).show();
		$('.response_throbber', $(this.el)).hide();


		// adds curl output
		var curlCommand = this.model.asCurl(this.map, {responseContentType: contentType});
		curlCommand = curlCommand.replace('!', '&#33;');
		$( 'div.curl', $(this.el)).html('<pre>' + _.escape(curlCommand) + '</pre>');

		// only highlight the response if response is less than threshold, default state is highlight response
		var opts = this.options.swaggerOptions;

		if (opts.showRequestHeaders) {
		  var form = $('.sandbox', $(this.el)),
			  map = this.getInputMap(form),
			  requestHeaders = this.model.getHeaderParams(map);
		  delete requestHeaders['Content-Type'];
		  $('.request_headers', $(this.el)).html('<pre>' + _.escape(JSON.stringify(requestHeaders, null, '  ')).replace(/\n/g, '<br>') + '</pre>');
		}

		var response_body_el = $('.response_body', $(this.el))[0];
		// only highlight the response if response is less than threshold, default state is highlight response
		if (opts.highlightSizeThreshold && typeof response.data !== 'undefined' && response.data.length > opts.highlightSizeThreshold) {
		  return response_body_el;
		} else {
		  return hljs.highlightBlock(response_body_el);
		}
	};
	
	
});




})();
