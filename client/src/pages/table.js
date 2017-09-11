(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ui/core', 'jquery', 'ething', 'ui/infopanel', 'ui/tableviewer', 'css!./table'], factory);
    }
}(this, function (UI, $, EThing, Infopanel) {
	
	return {
		
		buildView: function(data){
		
			var $template = UI.Container.set('<div>');
			
			var table = this.table = EThing.arbo.findOneById(data.rid);
			
			if(table){
				
				UI.Header.setTitle(table.basename());
				
				Infopanel.enable();
				Infopanel.setResource(table);
				
				
				$template.tableViewer({
					table: table,
					pagination: {
						enable: true,
						itemsPerPage: 'lazy',
						lazyScrollTarget: 'body > .ui-container',
						lazyLoadingItemsPerRequest: 60
					},
					actions: {
						'rightPanelToggle':{
							fn: function(){
								Infopanel.toggle();
							},
							icon: 'info-sign',
							tooltip: 'toggle the right panel',
							right: true,
							buttonClass: 'link'
						}
					}
				});
				
				this.update = function(){
					$template.tableViewer('reload');
				};
				
				table.on('updated', this.update);
				
			} else {
				UI.show404();
			}
		
		},
		
		deleteView: function(){
			if(this.table){
				this.table.off('updated', this.update);
			}
		}
		
	};
}));