(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','form','ething','./resourceselect','bootstrap-typeahead'], factory);
    } else {
        // Browser globals
        factory(root.jQuery,root.Form,root.EThing);
    }
}(this, function ($, Form, EThing) {
	
	
	
	
	function b64toBlob(b64Data, contentType, sliceSize) {
	  contentType = contentType || '';
	  sliceSize = sliceSize || 512;

	  var byteCharacters = atob(b64Data);
	  var byteArrays = [];

	  for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
		var slice = byteCharacters.slice(offset, offset + sliceSize);

		var byteNumbers = new Array(slice.length);
		for (var i = 0; i < slice.length; i++) {
		  byteNumbers[i] = slice.charCodeAt(i);
		}

		var byteArray = new Uint8Array(byteNumbers);

		byteArrays.push(byteArray);
	  }

	  var blob = new Blob(byteArrays, {type: contentType});
	  return blob;
	}
	
	
	
	
	var HttpRequest = {};
	
	// form builder
	HttpRequest = function(options){
		
		options = options || {};
		
		var relative = !!options.relative;
		var baseUrl = options.baseUrl || '';
		if(baseUrl){
			baseUrl = baseUrl.replace('/\/$/','');
			relative = true;
		}
		
		var methods = options.methods || ['GET','POST','PUT','PATCH','DELETE'];
		
		var layoutItems = [];
		
		
		layoutItems.push({
			name: 'method',
			item: new Form.Select({
				items: methods,
				name: 'method'
			}),
			hidden: methods.length===1
		});
		
		layoutItems.push({
			name: 'url',
			label: relative ? 'path' : 'url',
			item: new Form.Text({
				name: 'url',
				validators: relative ? [] : [Form.validator.NotEmpty, Form.validator.Url],
				placeholder: relative ? 'path/example?query' : 'http://example.com',
				format: relative ? {
					'out': function(value){
						// append the baseUrl
						return baseUrl + '/' + value.replace('/^\//','');
					},
					'in': function(value){
						// remove the baseUrl
						return value.indexOf(baseUrl)===0 ? value.replace(baseUrl,'') : value;
					}
				} : {}
			})
		});
		
		if(!options.noauth){
			
			layoutItems.push({
				name: 'auth',
				label: 'authentication',
				item: new Form.FormLayout({
					name: 'auth',
					items: [
						{
							name: 'type',
							item: new Form.Select(['basic','digest'])
						},{
							name: 'user',
							item: new Form.Text({
								validators: [Form.validator.NotEmpty],
								placeholder: 'user'
							})
						},{
							name: 'password',
							item: new Form.Text({
								password: true,
								validators: [Form.validator.NotEmpty],
								placeholder: 'password'
							})
						}
					]
				}),
				checkable: true,
				check: false
			});
			
		}
		
		if(options.headers !== false){
			layoutItems.push({
				name: 'headers',
				item: new Form.ArrayLayout({
					name: 'headers',
					editable: true,
					instanciator: function(){
						return new Form.FormLayout({inline: false, items: [{
							label: false,
							name: 'header',
							item: new Form.Text({
								name: 'header',
								validators: [Form.validator.NotEmpty],
								placeholder: 'header',
								onload: function(){
									this.$input.typeahead({
										source: Object.keys(HttpRequest.headersList),
										showHintOnFocus: true,
										items: 'all',
										fitToElement: true
									});
									
									var headerValueItem = this.parent().findItem('headervalue');
									this.change(function(){
										var header = this.value();
										headerValueItem.$input.typeahead('destroy').typeahead({
											source: HttpRequest.headersList[header] || [],
											showHintOnFocus: true,
											items: 'all',
											fitToElement: true
										});
									});
								}
							})
						},{
							name: 'value',
							label: false,
							item: new Form.Text({
								name: 'headervalue',
								validators: [Form.validator.NotEmpty],
								placeholder: 'value'
							})
						}]});
					},
					format: {
						'out': function(value){
							var headers = {};
							(value||[]).forEach(function(h){
								headers[h.header] = h.value;
							});
							return headers;
						},
						'in': function(value){
							var harr = [];
							for(var i in value){
								harr.push({
									header: i,
									value: value[i]
								});
							}
							return harr;
						}
					}
				}),
				checkable: true,
				check: false
			});
		}
		
		
		if(options.body !== false){
			
			var modes = Array.isArray(options.body) ? options.body : ['plain', 'binary', 'resource'];
			
			var bodyItems = [];
			
			if(modes.indexOf('plain') !== -1)
				bodyItems.push({
					name: 'plain',
					item: new Form.Textarea()
				});
			
			if(modes.indexOf('binary') !== -1)
				bodyItems.push({
					name: 'binary',
					label: 'local file',
					item: new Form.File({
						base64: true,
						validators: [Form.validator.NotEmpty]
					})
				});
			
			if(modes.indexOf('resource') !== -1)
				bodyItems.push({
					name: 'resource',
					item: new Form.ResourceSelect({
						filter: function(r){
							return r instanceof EThing.File || r instanceof EThing.Table;
						},
						validators: [Form.validator.NotEmpty]
					})
				});
			
			var bodyForm = {
				name: 'body',
				checkable: true
			};
			
			if(bodyItems.length>1){
				bodyForm.item = new Form.SelectPanels({
					items: bodyItems
				});
			}
			else if(bodyItems.length===1){
				bodyForm.item = bodyItems.item;
				bodyForm.format = {
					'out': function(value){
						return {
							type: bodyItems.name,
							value: value
						};
					},
					'in': function(value){
						return value.value;
					}
				};
			}
			
			if(bodyForm.item)
				layoutItems.push(bodyForm);
		}
		
		
		Form.Wrapper.call(this, {
			item : new Form.FormLayout({
				name: 'urlForm',
				items: layoutItems,
				onload: function(){
					var self = this;
					this.findItem('method').change(function(){
						self.toggle('body', this.value()!='GET' );
					});
				}
			}),
			value: options.value
		});
		
	};
	HttpRequest.prototype = Object.create(Form.Wrapper.prototype);
	
	HttpRequest.prototype.createView = function(){
		return Form.Wrapper.prototype.createView.call(this).addClass('f-httprequest');
	}
	
	HttpRequest.contentTypesList = [
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
	HttpRequest.headersList = {
		"Content-Type": HttpRequest.contentTypesList,
		"Accept": HttpRequest.contentTypesList,
		"Cookie": null,
		"Connection": ["keep-alive","close",""],
		"Authorization": null,
		"Origin": null,
		"Host": null,
		"Content-Length": null,
		"Accept-Encoding": null,
		"Transfer-Encoding": ["chunked", "compress", "deflate", "gzip", "identity"],
		"Accept-Charset": null,
		"Accept-Language": null,
		"Accept-Datetime": null,
		"Cache-Control": null,
		"Content-MD5": null,
		"Date": null,
		"Expect": null,
		"Forwarded": null,
		"From": null,
		"If-Match": null,
		"If-Modified-Since": null,
		"If-None-Match": null,
		"If-Range": null,
		"If-Unmodified-Since": null,
		"Max-Forwards": null,
		"Pragma": null,
		"Proxy-Authorization": null,
		"Range": null,
		"Referer": null,
		"User-Agent": null,
		"Upgrade": null,
		"Via": null,
		"Warning": null
	};
	
	
	/**
	*
	* Create a request Object from an options Object. It will indeed generate the body part.
	*
	**/
	HttpRequest.createRequest = function(opt, doneCb, failCb){
		
		var options = $.extend({}, opt), body = null, headers = $.extend({}, options.headers), hasContentTypeSet = false, dfr = $.Deferred();
		
		
		if($.isPlainObject(headers)){
			for(var i in headers){
				if(/^content-type$/i.test(i))
					hasContentTypeSet = true;
			}
		}
		
		if($.isPlainObject(options.body)){
			switch(options.body.type){
				case 'plain':
					body = options.body.value;
					if(!hasContentTypeSet) headers['Content-Type'] = 'text/plain';
					break;
				case 'binary':
					body = b64toBlob(options.body.value);
					if(!hasContentTypeSet) headers['Content-Type'] = body.type;
					break;
				case 'resource':
					var resource = EThing.arbo.findOneById(options.body.value);
					if(resource instanceof EThing.File){
						body = resource.read(true);
						if(!hasContentTypeSet) headers['Content-Type'] = resource.mime();
					}
					else if(resource instanceof EThing.Table){
						body = JSON.stringify(resource.select());
						if(!hasContentTypeSet) headers['Content-Type'] = 'application/json';
					}
					else if(resource instanceof EThing.App){
						body = resource.read();
						if(!hasContentTypeSet) headers['Content-Type'] = 'text/html';
					}
					break;
			}
		}
		
		$.when(body).then(function(bodyValue){
			delete options.body;
			options.data = bodyValue;
			dfr.resolve(options);
		}, function(err){
			dfr.reject(err || 'error');
		});
		
		return dfr;
		
	}
	
	HttpRequest.execute = function(options, doneCb, failCb){
		
		return HttpRequest.createRequest(options).then(function(req){
			
			if(req.auth){
				req.headers['X-AUTH'] = encodeURIComponent(req.auth.type) + ';' + encodeURIComponent(req.auth.user) + ';' + encodeURIComponent(req.auth.password);
				delete req.auth;
			}
			
			req.url = 'proxy?url='+encodeURIComponent(req.url);
			
			return EThing.request(req);
			
		}).done(doneCb).fail(failCb);
		
	}
	
	
	/* register as a Form plugin */
	Form.HttpRequest = HttpRequest;
	
	
	
	
}));