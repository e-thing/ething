(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    }
}(this, function ($) {
	
	
	return {
		
		require: ['widget/Buttons'],
		
		instanciate: function(device, options, Buttons){
			
			options = $.extend(true, {
				readonly: false,
				pollingRefreshPeriod: 30000
			}, options);
			
			var destroyFn = {};
			var readonly = !!options.readonly;
			var pollingRefreshPeriod = options.pollingRefreshPeriod || 30000;
			
			
			var widget = Buttons({
				buttons: [{
					label: 'On',
					onClick: function(){
						onViewStatusChanged(true);
					}
				},{
					label: 'Off',
					onClick: function(){
						onViewStatusChanged(false);
					}
				}],
				title: device.basename(),
				readonly: readonly
			});
			
			

			function getDeviceStatus(callback, fallback){
				
				if(device.data().hasOwnProperty('status')){
					callback(device.data('status'));
					return;
				}
				
				if(device.methods().hasOwnProperty('getStatus')){
					device.execute('getStatus').then(callback, fallback);
					return;
				}
				
				// unable to get data
				fallback('no data');
			}

			function setDeviceStatus(status, callback, fallback){
				if(!readonly) {
					device.execute(status ? 'on' : off).then(callback, fallback);
					return;
				}
				fallback('not capable');
			}

			function onViewStatusChanged(status){
				// is fired, each time the user change the state of the view
				
				// start loader
				toggleLoader(true);
				// disable buttons
				toggleView(false);
				
				function always(){
					// remove loader
					toggleLoader(false);
					// enable buttons
					toggleView(true);
				}
				
				function success(){
					always();
					setViewStatus(status);
				}
				
				function error(){
					always();
					setViewStatus(!status); // restore the old value !
				}
				
				setDeviceStatus(status, success, error);
				
			}

			function setViewStatus(status){
				widget.setActiveBtn(status ? 0 : 1);
				widget.setFooter(device.modifiedDate().toLocaleString());
			}

			function notifyViewError(message){
				
			}

			function toggleView(enable){
				widget.setEnabled(enable);
			}

			function toggleLoader(enable){
				
			}

			function updateView(){
				
				function set(status){
					// update the view state here
					setViewStatus(status);
				}
				
				function error(err){
					// unable to get the data : notify the user
					notifyViewError(err.toString());
				}
				
				getDeviceStatus(set, error);
			}

			function setRefreshStrategy(){
				
				if(device.data().hasOwnProperty('status')){
					
					// update the view each time the data attribute change.
					var resourceUpdate = function(event, updatedAttributes){
						if(updatedAttributes.indexOf('data')!==-1){
							updateView();
						}
					}
					device.on('updated', resourceUpdate);
					
					destroyFn['resourceUpdate'] = function(){
						device.off('updated', resourceUpdate);
					};
				} else if(device.methods().hasOwnProperty('getStatus')){
					
					// polling mode !
					var timerId = setInterval(function(){
						updateView();
					}, pollingRefreshPeriod);
					
					destroyFn['pollingRefresh'] = function(){
						clearInterval(timerId);
					};
				}
				
			}

			function destroy(){
				for(var i in destroyFn){
					destroyFn[i].call(this);
				}
			}
			
			
			return $.extend({}, widget, {
				
				draw: function(){
					
					widget.draw.call(this);
					
					updateView();
					setRefreshStrategy();
				},
				
				destroy: function(){
					destroy();
					widget.destroy.call(this);
				}
				
			});
			
		}
		
	};
	
	
}));