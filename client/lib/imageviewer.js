(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','ething','js/ui'], factory);
    } else {
        // Browser globals
        root.Form = factory(root.jQuery, root.EThing);
    }
}(this, function ($,EThing,UI) {


//var dependency = $.Dependency('//cdn.rawgit.com/exif-js/exif-js/master/exif.js');


var MOBILE_REGEX = /mobile|tablet|ip(ad|hone|od)|android/i;

var SUPPORT_TOUCH = ('ontouchstart' in window);
//var SUPPORT_POINTER_EVENTS = prefixed(window, 'PointerEvent') !== undefined;
var SUPPORT_ONLY_TOUCH = SUPPORT_TOUCH && MOBILE_REGEX.test(navigator.userAgent);



function insertAtIndex($parent, $child, index) {
    if(index === 0) {
     $parent.prepend($child);        
     return;
    }

	$parent.children().eq(index).before($child);
}

var blobToImage = function(blob){
	// build an image from the blob data
	var urlCreator = window.URL || window.webkitURL;
	var imageUrl = urlCreator.createObjectURL( blob );
	
	var image = new Image();
	image.src = imageUrl;
	return image;
};


var defaultOptions = {
	elements: [], // array of elements to be shown in the gallery, see below for details
	ajax:{
		headers: null, // header to be sent for each http request
		client: null
	},
	index: 0, // the index of the picture to be shown, default to the first one
	navigator:{
		enable: true, // enable the navigator, the navigator is disabled by default if the elements size is 1 or 0
		loadOnAppear: true, // load the thumbnail image only when the thumbnail is visible in the viewport, avoid to load all the thumbnail in the same time
		event: {} // event to be bind on each thumbnail
	},
	preload: false // if true, the previous image and the next one of the current image will be also loaded. 'next' to load only the next one. 'prev' to load only the previous one.
};

var defaultElementOptions = {
	name: null, // string
	content: null, // blob|Image|Resource|string|function(elementOptions) , load the content of the image, (if string ==> url)
	url: null, // string|function(elementOptions)->string , work only if 'content' attribute is not set
	thumbnailUrl: null, // string|function(elementOptions)->string , if not set, no thumbnail will be shown
	meta: null // object , a key-value pairs object of metadata concerning the image to be shown when the user ask to show the property of the image
};



var defaultHttpClient = function(url, options){
	return EThing.request({
		url : url,
		dataType: 'blob',
		headers: options.headers,
		cache: true
	});
}

var defaultMeta = function(img){
	var meta = {};
	
	if(img instanceof EThing.File){
		$.extend(meta,{
			'name': img.name(),
			'size' : UI.sizeToString(img.size()),
			'mime' : img.mime(),
			'created' : UI.dateToString(img.createdDate()),
			'modified' : UI.dateToString(img.modifiedDate())
		});
	}
	else if(typeof img == 'string'){ // url
		var url = img;
		$.extend(meta,{
			'name': url.split('/').pop().split('?').shift()
		});
	}
	
	return meta;
}

var getNaturalResolution = function(img, cb){
	if(typeof img.naturalWidth != 'undefined' && img.naturalWidth != 0)
		cb(img.naturalWidth,img.naturalHeight);
	else {
		var i = new Image;
		i.src = img.src;
		
		i.onload = function(){
			cb(this.width,this.height);
		}
	}
}

// cf: https://css-tricks.com/the-javascript-behind-touch-friendly-sliders/
var Slider = function(element, options){
	this.$element = $(element);
	var self = this;
	
	this.options = $.extend(true,{
		change: null
	},options);
	
	this.index = 0;
	
	
	
	var events = {
		start: function (event) {
			self.longTouch = false;
			delete self.movex;
			setTimeout(function () {
				self.longTouch = true;
			}, 250);
			self.touchstartx = event.originalEvent.touches[0].pageX;
			self.$element.removeClass('iv-animate');
		},
		move: function (event) {
			var width = self.width();
			self.touchmovex = event.originalEvent.touches[0].pageX;
			self.movex = self.index * width + (self.touchstartx - self.touchmovex);
			var panx = 100 - self.movex / 6;
			if (self.movex < width*(self.length-1)) {
				self.$element.css('transform', 'translate3d(-' + self.movex + 'px,0,0)');
			}
		},
		end: function (event) {
			if(typeof self.movex == 'undefined') return; // no movement
			var slideWidth = self.width(), index = self.index;
			var absMove = Math.abs(self.index * slideWidth - self.movex);
			if (absMove > slideWidth / 2 || self.longTouch === false) {
				if (self.movex > self.index * slideWidth) {
					index++;
				} else if (self.movex < self.index * slideWidth && self.index > 0) {
					index--;
				}
			}
			self.go(index);
		}
	}
	
	this.update();
	
	this.$element.on('touchstart.slider', function (event) {
		events.start(event);
	});
	this.$element.on('touchmove.slider', function (event) {
		events.move(event);
	});
	this.$element.on('touchend.slider', function (event) {
		events.end(event);
	});
	
	this._resizeHandler = function(){
		self.redraw();
	}
	
	$(window).on('resize.slider', this._resizeHandler);
	
}
Slider.prototype.width = function(){
	return this.$element.width() / this.length;
}
Slider.prototype.update = function(){
	this.length = this.$element.children().length;
	this.$element.css('width',(this.length*100)+'%');
	this.$element.children().css('width',(100/this.length)+'%');
}
Slider.prototype.redraw = function(){
	this.$element.removeClass('iv-animate').css('transform', 'translate3d(-' + this.index * this.width() + 'px,0,0)');
}
Slider.prototype.set = function(index){
	if(index<0) index=0;
	if(index>= this.length) index = this.length-1;
	this.index = index;
	this.$element.addClass('iv-animate').css('transform', 'translate3d(-' + this.index * this.width() + 'px,0,0)');
}
Slider.prototype.go = function(index){
	var oldindex = this.index;
	this.set(index);
	if(oldindex!=this.index && typeof this.options.change == 'function')
		this.options.change.call(this,index);
}
Slider.prototype.next = function(){
	this.go(this.index+1);
}
Slider.prototype.prev = function(){
	this.go(this.index-1);
}
Slider.prototype.destroy = function(){
	this.$element.off('touchstart.slider');
	this.$element.off('touchmove.slider');
	this.$element.off('touchend.slider');
	$(window).off('resize.slider', this._resizeHandler);
	this.$element.removeClass('iv-animate');
	this.$element.css({
		'transform': '',
		'width': ''
	});
}
	
var ImageViewer = function(element,options) {
	
	var self = this;
	
	this.$element = $(element);
	this.options = $.extend(true,{},defaultOptions,options);
	
	this.$element.empty();
	
	this.$element
		.removeClass('iv-nonav iv-fullscreen')
		.addClass('ImageViewer');
	
	
	this._elements = [];
	
	var $view = $('<div class="iv-view">'),
		$ui = $('<div class="iv-ui">'),
		$meta = $('<div class="iv-meta">').hide(),
		$navigator = $('<div class="iv-navigator">'),
		$header = $('<div class="iv-header">'),
		$title = $('<div class="iv-title">'),
		$actions = $('<div class="iv-actions">');
	
	this.$element.append($view,$ui);
	$ui.append($header,$meta,$navigator);
	$header.append($title, $actions);
	
	$('<span class="glyphicon glyphicon-resize-full iv-action-fullscreen" title="fullscreen" aria-hidden="true">').click(function(){
		self.toggleFullscreen();
	}).appendTo($actions);
	
	$('<span class="glyphicon glyphicon-download iv-action-download" title="download" aria-hidden="true">').click(function(){
		
		
		var $img = self.$element.find('.iv-cntr').children().eq(self.currentIndex()).find('img');
		if($img.length){
			var img = $img[0], element = self.currentElement();
			
			
			
			var hyperlink = document.createElement('a');
			hyperlink.href = img.src;
			hyperlink.target = '_blank';
			hyperlink.download = (element.name || element.meta.name || 'image').replace( /.*\//,'');
			
			
			if (!!navigator.mozGetUserMedia) {
				hyperlink.onclick = function() {
					(document.body || document.documentElement).removeChild(hyperlink);
				};
				(document.body || document.documentElement).appendChild(hyperlink);
			}
			
			//This is true only for IE,firefox
			var evt;
			if(document.createEvent){
			    // To create a mouse event , first we need to create an event and then initialize it.
				evt = document.createEvent("MouseEvent");
				evt.initMouseEvent("click",true,true,window,0,0,0,0,0,false,false,false,false,0,null);
			}
			else{
				 evt = new MouseEvent('click', {
							'view': window,
							'bubbles': true,
							'cancelable': true
						});
			}

			hyperlink.dispatchEvent(evt);

			if (!navigator.mozGetUserMedia) {
				URL.revokeObjectURL(hyperlink.href);
			}
			
		}
		
	}).appendTo($actions);
	
	/*$('<span class="glyphicon glyphicon-info-sign iv-action-toggle-meta" title="info" aria-hidden="true">').click(function(){
		
		var $img = self.$element.find('.iv-view').find('img');
		if($img.length && $img.data('data')){
			dependency.require(function(){
				
				EXIF.getData($img[0], function() {
					console.log(arguments);
					console.log(EXIF.pretty(this));
				});
				
			});
		}
		
		$meta.toggle();
	}).appendTo($actions);*/
	
	$('<span class="glyphicon glyphicon-refresh iv-action-toggle-reload" title="reload" aria-hidden="true">').click(function(){
		
		self.refresh();
		
	}).appendTo($actions);
	
	
	
	$view.append(
		'<div class="iv-cntr">'
	);
	
	this.slider = new Slider(this.$element.find('.iv-cntr'),{
		change: function(index){
			self.show(index);
		}
	});
	
	if(!SUPPORT_TOUCH){
		// add prev and next buttons
		$('<div class="iv-prev"><span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span></div>').click(function(e){
			self.previous();
			e.stopPropagation();
			return false;
		}).prependTo($view);
		$('<div class="iv-next"><span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span></div>').click(function(e){
			self.next();
			e.stopPropagation();
			return false;
		}).appendTo($view);
	}
	
	
	if(this.options.navigator.enable){
		
		require(['jquery.mousewheel'],function(){
			$navigator.mousewheel(function(event, delta) {
				if($navigator.css('overflow-x')!=='hidden'){
					this.scrollLeft -= (delta * 60);
					event.preventDefault();
				}
			});
		});
	
		// load thumbnail only when visible
		if(this.options.navigator.loadOnAppear){
			var check_lock = false;
			var appear_offset = 128;
			this._checkVisible = function(){
				if (check_lock) {
					return;
				}
				check_lock = true;
				
				setTimeout(function(){
					check_lock = false;
					$navigator.children().each(function(i){
						
						// is visible ?
						var $element = $(this),
							state = $element.data('state');
						if (state===1 || !$element.is(':visible'))
							return;

						var offset = $element.position();
						var left = offset.left;
						var top = offset.top;
							
						if (
							left + $element.width() + appear_offset >= 0 &&
							left - appear_offset <= $navigator.width() &&
							top + $element.height() + appear_offset >= 0 &&
							top - appear_offset <= $navigator.height()
						) {
							$element.data('state',1);
							$element.trigger('appear');
						}
							
						
					});
				}, 250);
			}
			$navigator.scroll(this._checkVisible);
			$(window).on('resize.imageviewer',this._checkVisible);
		}
		
	}
	
	// cached image loader
	
	this._loadImage = function(url) {
		var options = self.options.ajax;
		return typeof options.client == 'function' ? options.client(url,options) : defaultHttpClient(url,options);
	};
	
	
	setTimeout(function(){
		
		self.setItems(self.options.elements, self.options.index);		
		
	},1)

};

ImageViewer.prototype.destroy = function(){
	
	this.toggleFullscreen(false);
	
	this.slider.destroy();
	this.$element.empty();
	
	this.$element.removeClass('iv-nonav iv-fullscreen ImageViewer');
	$(document.body).removeClass('iv-fullscreen');
	
	$(document).off("keyup",this._keyupHandler);
	this.$element.off("mousemove",this._showHandler);
	
	$(window).off('resize.imageviewer',this._checkVisible);
	
	this.$element.removeData('imageViewer');
}

ImageViewer.prototype.setItems = function(items, index){
	
	var self = this,
		$cntr = this.$element.find('.iv-cntr'),
		$navigator = this.$element.find('.iv-navigator');
	
	// clear
	this._elements = [];
	$cntr.empty();
	$navigator.empty();
	
	
	
	if(!$.isArray(items))
		items = [items];
	
	var showNavigator = this.options.navigator.enable && items.length>1;
	
	if(!showNavigator)
		// no navigator
		this.$element.addClass('iv-nonav');
		
	items.forEach(function(el, index){
		
		var $item = $('<div class="iv-item">').appendTo($cntr);
		
		if(!$.isPlainObject(el))
			el = {
				content: el
			};
		
		var element = $.extend(true,{},defaultElementOptions, el);
		
		if(!element.content)
			element.content = element.url;
		
		element.meta = $.extend({}, defaultMeta(element.content), element.meta);
		
		if(!element.thumbnailUrl && element.thumbnailUrl!==false){
			if(element.content instanceof EThing.File)
				element.thumbnailUrl = element.content.thumbnailLink();
		}
		
		$item.html('<div>'+(element.name || element.meta.name)+'</div>');
		
		element.state = 'pending';
		
		function setError(e){
			$item.removeClass('iv-vertical-align').html('<div class="error">error: '+(e && e.message ? e.message : (typeof e === 'string' ? e : 'unknown'))+'</div>');
			element.state = 'error';
			
			if(typeof callback == 'function')
				callback.call(self,element);
		}
		
		function asyncload(dfr, callback){
			dfr
				.done(function(img){
					setImage(img, callback);
				})
				.fail(setError)
				.progress(function(evt){
					if (evt.lengthComputable)
						$('.loader',$item).html(Math.round((evt.loaded / evt.total)*100)+'% loaded');
				});
		}
		
		function setImage(img, callback){
			
			if($.isPlainObject(img) && typeof img.promise == 'undefined'){ // an element object
				$.extend(true,element,img); // extend the actual property
				img = element.content;
			}
			
			$.extend(element.meta, defaultMeta(img)); // update the meta data
			
			if(typeof img == 'string'){ // url
				return asyncload( self._loadImage(img), callback );
			}
			else if(img instanceof EThing.File){
				return asyncload( img.read(true), callback );
			}
			else if(img instanceof Blob){
				img = blobToImage(img);
			}
			else if(typeof img.promise == 'function'){ // a deferred object
				return asyncload(img, callback);
			}
			
			
			var $image = $(img);
			
			$image.on('error',setError);
			
			$image.click(function(evt){
				if(!self.isFullscreen()){
					self.toggleFullscreen();
					evt.stopPropagation();
				}
			});
			
			$item.addClass('iv-vertical-align').html($image);
			
			// update meta information
			getNaturalResolution(img,function(width,height){
				var meta = $.extend(element.meta, {
					width: width+'px',
					height: height+'px'
				});
			});
			
			element.state = 'loaded';
			
			if(typeof callback == 'function')
				callback.call(self,element);
			
			if(typeof element.onload == 'function')
				element.onload.call(element);
			
		}
		
		element.load = function(callback){
			
			$item.html('<div>'+(element.name || element.meta.name)+'<div class="loader">0% loaded</div></div>');
			
			element.state = 'loading';
			
			$item.removeClass('iv-vertical-align');
			
			var content = (typeof element.content == 'function') ? element.content.call(self,element) : element.content;
			
			if(!content)
				content = typeof element.url == 'function' ? element.url.call(self,element) : element.url;
			
			setImage(content,callback);
			
		}
		
		
		// navigator
		if(showNavigator){
			var $d = $('<div>')
				.append('<span class="glyphicon glyphicon-picture" aria-hidden="true">');
			
			if(!SUPPORT_ONLY_TOUCH)
				$d.tooltip({
					container: this.$element,
					trigger:'hover',
					placement: 'top',
					title: function(){
						return (element.name || element.meta.name || 'untitled').replace( /.*\//,'');
					}
				})
				.on('show.bs.tooltip',function(e,a){
					// if the navigator is in the right, show the tooltip on the left
					$d.data('bs.tooltip').options.placement = $navigator.css('overflow-x')==='hidden' ? 'left' : 'top';
				});
			
			$d.click(function(evt){
				if(self.currentIndex() != index)
					self.show(index);
				evt.stopPropagation();
				evt.preventDefault();
				return false;
			});
			
			if(self.options.navigator.event)
				for(var e in self.options.navigator.event)
					$d.on(e,self.options.navigator.event[e]);
			
			$navigator.append($d);
			
			element.$nav = $d;
		}
		
		
		this._elements.push(element);
		
	}, this);
	
	
	
	this.slider.update();
	
	
	if(this._elements.length){
		// show the first picture
		this.show(index || 0, false, function(){
			
			//load the thumbnails only after the first image was loaded
			if(showNavigator){
				self._elements.forEach(function(element, index){
					
					var thumbnailUrl = typeof element.thumbnailUrl == 'function' ? element.thumbnailUrl.call(self,element) : element.thumbnailUrl;
					
					if(typeof thumbnailUrl == 'string'){
						
						var show = function(){
							self
								._loadImage(thumbnailUrl)
								.done(function(blob){
									var $image = $(blobToImage(blob));
									
									element.$nav.html($image);
								});
						};
						
						if(self.options.navigator.loadOnAppear)
							element.$nav.on('appear',show);
						else
							show();
					}
					
				}, self)
				
				$navigator.trigger('scroll');
			}
			
		});
	} else {
		// empty !
	}
	
}
ImageViewer.prototype.show = function(index, forceRefresh, callback){
	var self = this;
	
	if(index < 0 || index >= this._elements.length)
		return this; // invalid index !
	
	var element = this._elements[index];
	if(!element)
		return this;
	
	var $title = $('.iv-header>.iv-title',this.$element).html(element.name || element.meta.name || 'loading...');
	
	var hasNext = index < (this._elements.length - 1);
	var hasPrevious = index > 0;
	
	$('.iv-next',this.$element).toggle(hasNext);
	$('.iv-prev',this.$element).toggle(hasPrevious);
	
	var onload = function(){
		
		if(typeof callback == 'function')
			callback.call(self,element);
		
		// pre load the next image
		if(hasNext && (self.options.preload===true || /next/i.test(self.options.preload))){
			var nextElement = self._elements[index+1];
			if(nextElement.state === 'pending')
				nextElement.load();
		}
		// pre load the previous image
		if(hasPrevious && (self.options.preload===true || /prev/i.test(self.options.preload))){
			var prevElement = self._elements[index-1];
			if(prevElement.state === 'pending')
				prevElement.load();
		}
		
		self.$element.trigger('shown.imageviewer',[element,index]);
	}
	
	this.index = index;
	
	if(this.slider.index != this.index)
		this.slider.set(this.index);
	
	this.$element.trigger('show.imageviewer',[element,index]);
	
	if(element.state === 'pending' || (forceRefresh && element.state != 'loading'))
		element.load(function(element){
			if(self.index != index) return;
			
			// update title
			$title.html(element.name || element.meta.name || 'untitled');
			
			onload();
		});
	else if(element.state === 'loading'){
		var p_onload = element.onload || null;
		element.onload = function(){
			this.onload = p_onload;
			onload();
		}
	}
	else if(element.state === 'loaded')
		onload();
	
	
	return this;
}
ImageViewer.prototype.refresh = function(){
	return this.show(this.currentIndex(),true);
}
ImageViewer.prototype.currentIndex = function(){
	return this.index;
}
ImageViewer.prototype.next = function(){
	return this.show(this.currentIndex()+1);
}
ImageViewer.prototype.previous = function(){
	return this.show(this.currentIndex()-1);
}
ImageViewer.prototype.currentElement = function(){
	return this._elements[this.currentIndex()];
}
ImageViewer.prototype.isFullscreen = function(){
	return this.$element.hasClass('iv-fullscreen');
}
ImageViewer.prototype.toggleFullscreen = function(state){
	var isFullscreen = this.isFullscreen(),
		self = this;
	
	if(typeof state != 'undefined' && state == isFullscreen)
		return;
	
	var $view = this.$element.find('.iv-view'),
		$ui = this.$element.find('.iv-ui, .iv-prev>span, .iv-next>span');
	
	
	function showAutoHide(){
		$ui.fadeIn(400);
		if(self.fsuito) clearTimeout(self.fsuito);
		self.fsuito = setTimeout(function(){
			$ui.fadeOut(400); // auto hide the ui layer after a N seconds
		},5000);
	}
	
	if(!this._keyupHandler){
		this._keyupHandler = function(e) {
			 e.preventDefault();
		     e.stopImmediatePropagation();
			 if (e.keyCode == 27){ // escape key maps to keycode `27`
				self.toggleFullscreen(false);
			 }
			 return false;
		};
	}
	if(!this._showHandler){
		this._showHandler = function(e) {
			if(e.type == "mousemove" && self._mousemoveCoord && self._mousemoveCoord.x == e.pageX && self._mousemoveCoord.y == e.pageY) return;
			self._mousemoveCoord = {
				x: e.pageX,
				y: e.pageY
			};
			showAutoHide();
		};
	}
	if(!this._exitHandler){
		this._exitHandler = function(e) {
			self.toggleFullscreen(false);
		};
	}
	
	if(!isFullscreen){
		this.$parent = this.$element.parent();
		this.indexInParent = this.$element.index();
		this.$element.appendTo(document.body);
	} else {
		insertAtIndex(this.$parent, this.$element, this.indexInParent);
	}
	
	var $viewport = $('meta[name="viewport"]');
	if(!isFullscreen){
		this.viewportContent = $viewport.attr('content');
		$viewport.attr('content', 'width=device-width, initial-scale=1');
	} else {
		$viewport.attr('content', this.viewportContent);
	}
	
	this.$element.toggleClass('iv-fullscreen',!isFullscreen);
	
	$(document.body).toggleClass('iv-fullscreen',!isFullscreen);
	
	// force resize
	$(window).resize();
	
	
	if(isFullscreen){
		$(document).off("keyup",this._keyupHandler);
		this.$element.off("mousemove",this._showHandler);
		this.$element.find('.iv-navigator').off("scroll",this._showHandler);
		$view.off("click",this._showHandler);
		$view.off("dblclick",this._exitHandler);
		if(this.fsuito) clearTimeout(this.fsuito);
		$ui.show();
	}
	else {
		// make it fullscreen
		$(document).on("keyup",this._keyupHandler);
		this.$element.on("mousemove",this._showHandler);
		this.$element.find('.iv-navigator').on("scroll",this._showHandler);
		$view.on("click",this._showHandler);
		$view.on("dblclick",this._exitHandler);
		showAutoHide();
	}
	
	// update action icon
	if(self.isFullscreen())
		self.$element.find('.iv-action-fullscreen').addClass('glyphicon-resize-small').removeClass('glyphicon-resize-full');
	else
		self.$element.find('.iv-action-fullscreen').removeClass('glyphicon-resize-small').addClass('glyphicon-resize-full');
}



/* register as a plugin in jQuery */

$.ImageViewer = ImageViewer;

$.fn.imageViewer = function(){
	var args = [].slice.call(arguments);
	
	if (this[0]) { // this[0] is the renderTo div
		
		var instance = $(this[0]).data('imageViewer');
		
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
		instance = new ImageViewer(this[0],args[0],args[1],args[2],args[3],args[4],args[5],args[6]);
		$(this[0]).data('imageViewer',instance);
		
		return this;
	}
};


return ImageViewer;

}));