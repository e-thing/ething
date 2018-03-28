(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','ui/widget', 'css!switch'], factory);
    }
}(this, function ($, Widget) {
	
	
	function Switch(opt){
		
		opt = opt || {};
		
		var parent = Widget(opt);
		
		var self = {};
		
		var value = typeof opt.value == 'undefined' ? false : !!opt.value;
		var onChange = opt.onChange || function(){};
		var doneText = function(){
			return 'done';
		};
		var errText = function(){
			return 'error';
		};
		
		if(typeof opt.doneText == 'string')  doneText = function(){ opt.doneText };
		else if(typeof opt.doneText != 'undefined') doneText = opt.doneText;
		if(typeof opt.errText == 'string')  errText = function(){ opt.errText };
		else if(typeof opt.errText != 'undefined') errText = opt.errText;
		
		var _infoTextTimeout = null;
		var setInfoText = function(text,timeout){
			if(_infoTextTimeout) clearTimeout(_infoTextTimeout);
			_infoTextTimeout = null;
			self.$element.find('.info').text(text || '');
			if(timeout){
				_infoTextTimeout = setTimeout(function(){
					self.$element.find('.info').text('');
				}, timeout);
			}
		}
		
		var setEnabled = function(enabled){
			self.$element.find('.switch').toggleClass('switch-disabled', !enabled);
		};
		
		var execute = function(state){
			setEnabled(false);
			setInfoText('wait...');
			
			return $.when(onChange(state)).done(function(v){
				if(doneText) setInfoText(doneText(v), 2000);
				else setInfoText();
			}).fail(function(err){
				if(errText) setInfoText(errText(err), 2000);
				else setInfoText();
			}).always(function(){
				setEnabled(true);
			});
		};
		
		return $.extend(self, parent, {
			
			draw: function(){
				
				parent.draw.call(this);
				
				var $switch = $('<a href="#" class="switch"></a>').css({
					'width': '80%',
					'max-width': '200px',
					'font-size': '15px'
				});
				
				
				
				$switch.click(function(e) {
					var $this = $(this),
						state = !$this.hasClass('switch-on');
					
					e.preventDefault();
					
					if($this.hasClass('switch-disabled')) return;
					
					$this.toggleClass('switch-on', state)
					
					execute(state);
				});
				
				var $info = $('<div class="info">').css({
					'font-size': '12px',
					'position': 'absolute',
					'width': '100%'
				});
				
				this.$element.append(
					
					$('<div>').append(
						$switch,
						$info
					).css({
						'text-align': 'center',
						'position': 'relative',
						'width': '100%'
					})
				).attr('style','display: -webkit-box;display: -moz-box;display: -ms-flexbox;display: -webkit-flex;display: flex;').css({
					'display': 'flex',
					'-webkit-flex-direction': 'column',
					'-moz-flex-direction': 'column',
					'-ms-flex-direction': 'column',
					'-o-flex-direction': 'column',
					'flex-direction': 'column',
					'justify-content': 'center',
					'color': '#a3a3a3'
				});
				
			},
			
			val: function(v){
				value = !!v;
				this.$element.find('.switch').toggleClass('switch-on', value);
			}
			
		});
		
	}
	
	
	return Switch;
	
}));