(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','ething','./core','text!./infopanel.html','css!./infopanel','bootstrap','./browser'], factory);
    }
}(this, function ($, EThing, UI, template) {
	
	
	console.log('loading ./infopanel.js');
	
	
	var usageDfr;
	function getUsage(cb){
		if(!usageDfr)
			usageDfr = EThing.Resource.usage();
		
		usageDfr.done(function(usage){
			
			EThing.arbo.load(function(){
				
				$.extend(usage,{
					'nbResource': 0,
					'fileTotalSize': 0,
					'appTotalSize': 0,
					'tableTotalRowCount': 0
				});
				
				EThing.arbo.list().forEach(function(r){
					usage.nbResource++;
					
					var type = r.baseType(),
						metaname = 'nb'+type;
					
					if(!usage.hasOwnProperty(metaname))
						usage[metaname] = 0;
					usage[metaname]++;
					
					if(type==='File')
						usage.fileTotalSize += r.size();
					else if(type==='Table')
						usage.tableTotalRowCount += r.length();
					else if(type==='App')
						usage.appTotalSize += r.size();
					
				})
				
				if(typeof cb == "function")
					cb(usage);
			});
			
		});
		
	};
	
	
	
	var isMobile = function(){
		var $el = $('<div>').addClass('hidden-xs');;
		$el.appendTo($('body'));
		
		var isMobile = $el.is(':hidden');
		
		$el.remove();
		return isMobile;
	}
	
	var Infopanel = {
		$element : $(template),
		
		enable: function(){
			this.setResource(null);
			$('body').addClass('ui-rp');
		},
		
		disable: function(){
			$('body').removeClass('ui-rp ui-rp-mobile-shown ui-rp-desktop-hidden');
		},
		
		hide: function(){
			if(isMobile())
				$('body').removeClass('ui-rp-mobile-shown');
			else
				$('body').addClass('ui-rp-desktop-hidden');
		},
		show: function(){
			if(isMobile())
				$('body').addClass('ui-rp-mobile-shown');
			else
				$('body').removeClass('ui-rp-desktop-hidden');
		},
		isShown: function(){
			return isMobile() ? $('body').hasClass('ui-rp-mobile-shown') : !$('body').hasClass('ui-rp-desktop-hidden');
		},
		toggle: function(){
			this.isShown() ? this.hide(): this.show();
		},
		refresh: function(){
			if(this.resource) this.setResource(this.resource, true);
		},
		
		setResource: function(resource,forceUpdate){
			var self = this;
			var $rightPanelDetails = this.$element.find('#details');
			
			if(arguments.length==0){
				forceUpdate = true;
				resource = this.resource;
			}
			
			if(typeof resource === 'string'){
				resource = resource.split(',');
			}
			
			if($.isArray(resource)){
				resource = resource.map(function(r){
					return r instanceof EThing.Resource ? r : EThing.arbo.findOneById(r);
				}).filter(function(r){
					return !!r;
				});
			}
			
			if($.isArray(resource) && resource.length==1)
				resource = resource[0];
			
			var multiple = $.isArray(resource),
				selectionId = multiple ? (resource.length ? resource.map(function(r){return r.id();}).join(',') : null) : (resource ? resource.id() : null);
				
			
			if(!forceUpdate && this.resource===selectionId)
				return; // no change
			
			this.resource = selectionId;
			
			if(selectionId===null){ // no selection
				if($rightPanelDetails.is(':visible')){
					$rightPanelDetails.stop(true).slideUp(400,function(){
						$(this).hide();
					});
				}
				else if(!this.$element.is(':visible')){
					$rightPanelDetails.stop(true).hide();
				}
				return;
			}
			
			
			
			var $title = $('[data-role="title"]',$rightPanelDetails).empty(),
				$thumbnail = $('[data-role="thumbnail"]',$rightPanelDetails).empty(),
				$detail = $('[data-role="detail"]',$rightPanelDetails).empty(),
				$data = $('[data-role="data"]',$rightPanelDetails).empty().hide(),
				$action = $('[data-role="action"]',$rightPanelDetails).empty(),
				$description = $('[data-role="description"]',$rightPanelDetails).empty().hide();
			
			var props = null;
			
			if(multiple){
				// multiple selection
				
				var svg = '<svg viewBox="0 0 32 32" style="fill: #5959B6;"><circle cx="18" cy="14" r="14"></circle><circle cx="17" cy="15" r="14" fill="white"></circle><circle cx="16" cy="16" r="14"></circle><circle cx="15" cy="17" r="14" fill="white"></circle><circle cx="14" cy="18" r="14"></circle><text x="14" y="18" font-size="22" fill="white" font-weight="bold" font-family="Arial" text-anchor="middle" alignment-baseline="central">+</text></svg>';
				$thumbnail.html(svg);
				
				var $cntttl = $('<div style="white-space: normal;">'), maxTitleRows = 5;
				
				if(resource.length>maxTitleRows)
					$cntttl.html( resource.slice(0,maxTitleRows).map(function(r){return r.basename();}).join(',<br>')+'<small><br>...<br>+'+(resource.length-maxTitleRows)+' more</small>' );
				else
					$cntttl.html( resource.map(function(r){return r.basename();}).join(',<br>') );
				$title.html($cntttl);
				
				var totalSize = resource.reduce(function(size,r){return size + (r.size ? r.size() : 0);},0);
				
				props = {
					'size': UI.sizeToString(resource.reduce(function(size,r){return size + (r.size ? r.size() : 0);},0)),
					'length': resource.length+' resources'
				};
				
			}
			else { // single resource
			
				$title.html(resource.basename());
				$thumbnail.html($.Browser.generateSvgResourceIcon(resource));
				
				var imageUrl = (typeof resource.thumbnailLink == 'function') ? resource.thumbnailLink() : ((typeof resource.iconLink == 'function') ? resource.iconLink() : null);
				if(imageUrl){
					EThing.request({
						url: imageUrl,
						dataType: 'blob',
						cache: true
					}).done(function(blob){
						if(self.resource===resource.id()){
							// build an image from the blob data
							var urlCreator = window.URL || window.webkitURL;
							var imageUrl = urlCreator.createObjectURL( blob );
							
							var image = new Image();
							image.src = imageUrl;
							$thumbnail.html(image);
						}
					});
				}
				
			
				props = UI.getResourceFormattedValues(resource,{
					"createdBy":{
						formatter: function(createdBy){
							if(!createdBy)
								return 'Me';
							else {
								var createdByRess = EThing.arbo.findOneById(createdBy.id);
								if(createdByRess instanceof EThing.Device)
									return '<a href="#!device?rid='+createdByRess.id()+'">'+createdByRess.basename()+'</a>';
								else if(createdByRess instanceof EThing.Resource)
									return createdByRess.basename();
							}
						}
					}
				}, function(){
					return ["name","type","createdBy","createdDate","modifiedDate","lastSeenDate","size","mime","length","maxLength","expireAfter","battery","location","url","version","revision","build","isMetric","libVersion","transport","nodeId","sensorId","sensorType","sketchName","sketchVersion","smartSleep","topic","public","inclusion"].indexOf(this.name) >= 0;
				});
				
				// print the data
				var data = resource.data();
				for(var i in data){
					if(data[i]!==null){
						$('<div class="row">').append(
							'<div class="col-xs-4 ellipsis key">'+i+'</div>',
							$('<div class="col-xs-8 ellipsis value">').append(String(data[i]))
						).appendTo($data);
					}
				}
				if($data.children().length) $data.show();
				
			}
			
			// print the properties
			for(var i in props){
				if(props[i]!==null){
					$('<div class="row">').append(
						'<div class="col-xs-4 ellipsis key">'+i+'</div>',
						$('<div class="col-xs-8 ellipsis value">').append(props[i])
					).appendTo($detail);
				}
			}
			
			
			// print the actions
			
			UI.actions.forEach(function(action){
				if(action.filter(resource)){
					var $a = $('<button type="button" class="btn btn-default" aria-label="'+action.name+'">'+
								'<span class="glyphicon glyphicon-'+action.icon+'" aria-hidden="true"></span>'+
							'</button>');
					
					$a.click(function(){
						action.fn(resource);
					});
					
					if(!UI.isTouchDevice)
						$a.tooltip({
							container: $action,
							trigger:'hover',
							placement: 'bottom',
							title: action.name
						});

					$a.appendTo($action);
				}
			});
			
			// description
			var description = (!multiple && $.isFunction(resource.description)) ? resource.description() : null;
			if(description){
				$description.html(description.replace(/\n/g,'<br>')).show();
			}
			
			if(!$rightPanelDetails.is(':visible')){
				$rightPanelDetails.stop(true).slideDown(400,function(){
					$(this).show();
				});
			} else {
				$rightPanelDetails.stop(true).show();
			}
			
			
		},
		
		showDefault: function(){
			var id = String(Math.round(Math.random()*1000000)),
				$usage = this.$element.find('#usage').html('loading...').data('id',id);
			
			getUsage(function(usage){
				if(id != $usage.data('id')) return;
				
				var hasQuota = !!usage.quota_size,
					tableUsed = usage.used - usage.fileTotalSize - usage.appTotalSize,
					vquota = hasQuota ? usage.quota_size : usage.used,
					usedRatio = usage.used / vquota,
					fileUsedRatio = usage.fileTotalSize / vquota,
					appUsedRatio = usage.appTotalSize / vquota,
					tableUsedRatio = tableUsed / vquota;
					
				$usage.html(
					'<h2 class="usage-used">'+
						UI.sizeToString(usage.used)+' used'+
					'</h2>'+
					'<div class="usage-bar">'+
						'<div class="usage-bar-file" style="width: '+(Math.round(fileUsedRatio*100))+'%"></div>'+
						'<div class="usage-bar-table" style="width: '+(Math.round((fileUsedRatio+tableUsedRatio)*100))+'%"></div>'+
						'<div class="usage-bar-app" style="width: '+(Math.round(usedRatio*100))+'%"></div>'+ // else
					'</div>'+
					'<table class="usage-bar-detail">'+
						'<tr class="usage-bar-detail-file">'+
							'<td class="usage-bar-detail-color"></td>'+
							'<td class="usage-bar-detail-type">File</td>'+
							'<td class="usage-bar-detail-size">'+UI.sizeToString(usage.fileTotalSize)+'</td>'+
						'</tr>'+
						'<tr class="usage-bar-detail-table">'+
							'<td class="usage-bar-detail-color"></td>'+
							'<td class="usage-bar-detail-type">Table</td>'+
							'<td class="usage-bar-detail-size">'+UI.sizeToString(tableUsed)+'</td>'+
						'</tr>'+
						'<tr class="usage-bar-detail-app">'+
							'<td class="usage-bar-detail-color"></td>'+
							'<td class="usage-bar-detail-type">App</td>'+
							'<td class="usage-bar-detail-size">'+UI.sizeToString(usage.appTotalSize)+'</td>'+
						'</tr>'+
					'</table>'+
					'<h4 class="usage-count-title">Details :</h4>'+
					'<table class="usage-count">'+
						'<tr class="usage-count-file">'+
							'<td class="usage-count-value">'+(usage.nbFile || 0)+'</td>'+
							'<td class="usage-count-name">File'+(usage.nbFile > 1 ? 's' : '')+'</td>'+
						'</tr>'+
						'<tr class="usage-count-table">'+
							'<td class="usage-count-value">'+(usage.nbTable || 0)+'</td>'+
							'<td class="usage-count-name">Table'+(usage.nbTable > 1 ? 's' : '')+'</td>'+
						'</tr>'+
						'<tr class="usage-count-device">'+
							'<td class="usage-count-value">'+(usage.nbDevice || 0)+'</td>'+
							'<td class="usage-count-name">Device'+(usage.nbDevice > 1 ? 's' : '')+'</td>'+
						'</tr>'+
						'<tr class="usage-count-app">'+
							'<td class="usage-count-value">'+(usage.nbApp || 0)+'</td>'+
							'<td class="usage-count-name">App'+(usage.nbApp > 1 ? 's' : '')+'</td>'+
						'</tr>'+
					'</table>'
				);
			});
		}
	};
	
	
	// swipe 
	
	var $target = Infopanel.$element.find(".content"),
		longTouch,
		movex,
		touchstartx,
		disabled;
	
	$target.on('touchstart', function (event) {
		longTouch = false;
		movex = false;
		disabled = false;
		setTimeout(function () {
			longTouch = true;
		}, 250);
		touchstart = event.originalEvent.touches[0];
	});
	$target.on('touchmove', function (event) {
		if(disabled) return;
		var dx = event.originalEvent.touches[0].pageX - touchstart.pageX,
			dy = event.originalEvent.touches[0].pageY - touchstart.pageY,
			d = Math.sqrt(dx*dx+dy*dy);
		if(d>=20){
			if(movex===false){
				if(Math.abs(dy)>Math.abs(dx)){
					// vertical movement
					disabled=true;
					return;
				}
				$target.css('transition','none');
			}
			movex = dx;
			if(movex>0)
				$target.css('transform', 'translate3d(' + movex + 'px,0,0)');
		}
	});
	$target.on('touchend', function (event) {
		if(movex === false) return; // no movement
		if (movex > 0 && (movex > $target.width() / 2 || longTouch === false))
			Infopanel.hide();
		$target.css('transform', '');
		$target.css('transition','');
	});
	
	
	
	
	Infopanel.showDefault();
	
	UI.Infopanel = Infopanel;
	
	UI.$element.append(
		Infopanel.$element
	);
	
	UI.on('ui-pageChange', function(){
		Infopanel.disable(); // disabled by default !
	});
	
	EThing.on('ething.resource.removed',function(evt, r){
		if(typeof Infopanel.resource === 'string'){
			var rids = Infopanel.resource.split(','),
				i = rids.indexOf(r);
			if(i!==-1){
				rids.splice(i,1);
				Infopanel.setResource(rids);
			}
		}
	});
	
	EThing.on('ething.arbo.changed',function(evt){
		Infopanel.refresh();
	});
	
	return Infopanel;
}));