(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','jquery.knob','css!bootstrap-toggle-flat', 'css!titatoggle-extra'], factory);
    }
}(this, function ($) {
	
	var Dimmer = function(element, sensor){
		
		var self = this;
		
		this.$element = $(element);
		this.sensor = sensor;
		
		var color = 'white';
		var bgc = this.$element.css('background-color');
		
		var rgb = bgc.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)/);
		if(rgb){
			var luma = 0.2126 * parseInt(rgb[1]) + 0.7152 * parseInt(rgb[2]) + 0.0722 * parseInt(rgb[3]); // per ITU-R BT.709
			if (luma < 40) {
				color = '#a0a0a0';
			}
		}
		
		var $status = $('<div class="checkbox checkbox-slider--b-flat checkbox-slider-nolabel"><label><input type="checkbox" class="status"><span></span></label></div>');
		
		this.$element.append(
			$('<div>').append(
				$status.css({
					'margin-bottom': '0px'
				}),
				$('<input type="text" class="percentage">')
			).css({
				'margin': 'auto 0',
				'text-align': 'center'
			})
		).css({
			'display': 'flex',
			'color': 'white',
			'flex-direction': 'column'
		});
		
		this.$element.find('input.percentage').knob({
			cursor: 40,
			thickness: 0.2,
			fgColor: color,
			displayPrevious: true,
			width: "50%",
			/*width: 70,
			height: 70,*/
			draw : function () {

				this.cursorExt = 0.3;

				var a = this.arc(this.cv)  // Arc
						, pa                   // Previous arc
						, r = 1;

				this.g.lineWidth = this.lineWidth;

				if (this.o.displayPrevious) {
					pa = this.arc(this.v);
					this.g.beginPath();
					this.g.strokeStyle = this.pColor;
					this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, pa.s, pa.e, pa.d);
					this.g.stroke();
				}

				this.g.beginPath();
				this.g.strokeStyle = r ? this.o.fgColor : this.fgColor ;
				this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, a.s, a.e, a.d);
				this.g.stroke();

				this.g.lineWidth = 2;
				this.g.beginPath();
				this.g.strokeStyle = this.o.fgColor;
				this.g.arc( this.xy, this.xy, this.radius - this.lineWidth + 1 + this.lineWidth * 2 / 3, 0, 2 * Math.PI, false);
				this.g.stroke();

				return false;
			},
			'release' : function (v) {
				if(self.percentage !== v){
					self._execute('setPercentage',{
						percentage: v
					});
				}
			}
		});
		
		$status.find('input').change(function(){
			var $this = $(this),
				status = $this.prop('checked');
			
			self._execute(status ? 'on' : 'off');
		});
		
		this.update = function(){
			self.percentage = self.sensor.val('V_PERCENTAGE') || 0;
			self.status = self.sensor.val('V_STATUS') || false;
			
			self.$element.find('input.status').prop( "checked", self.status );
			self.$element.find('input.percentage').val(self.percentage).trigger('change');
		}
		
		this.update();
		
		this.sensor.on('updated',this.update);
		
	};
	
	Dimmer.prototype.destroy = function(){
		// remove any event handler
		this.$element.find('input.percentage').trigger('destroy'); // destroy knob instance
		this.sensor.off('updated', this.update);
	};
	
	Dimmer.prototype._execute = function(fn, data){
		var self = this;
		this.setEnabled(false);
		return this.sensor.execute(fn,data,function(response){
			if(response instanceof Error){
				console.log(response);
				if(typeof self.onerror == 'function')
					self.onerror.call(self, response);
			}
			
			self.sensor.update().done(function(){
				self.setEnabled(true);
			});
		});
	};
	
	Dimmer.prototype.setEnabled = function(enabled){
		enabled
			? this.$element.find('input.status').removeAttr("disabled")
			: this.$element.find('input.status').attr( "disabled", 'disabled' );
			
		this.$element.find('input.percentage').trigger('configure', {
			readOnly: !enabled
		});
	};
	
	return Dimmer;
	
}));