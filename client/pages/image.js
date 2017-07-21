(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['js/ui', 'jquery', 'ething', 'imageviewer', 'css!./image'], factory);
    }
}(this, function (UI, $, EThing) {
	
	return {
		
		buildView: function(data){
			
			var $template = this.$template = UI.Container.set('<div>');
			
			var resource = EThing.arbo.findOneById(data.rid);
			

			var directoryPath = resource ? resource.dirname() : EThing.arbo.root,
				loadIndex = null;
			
			// select only the image in the same folder
			var images = EThing.arbo.find(function(r){
				return r instanceof EThing.File && /^image\//.test(r.mime()) && r.dirname() === directoryPath;
			});
			
			if(resource){
				for(var i=0; i<images.length; i++){
					if(images[i].id()===resource.id()){
						loadIndex = i;
						break;
					}
				}
			}
			
			
			$template
				.on('show.imageviewer',function(ev,el){
					
					UI.setUrl('image',{
						rid: el.content.id()
					});
					
				})
				.imageViewer({
					elements: images,
					navigator:{
						enable: true
					},
					index: loadIndex
				});
			
			
			$(document).on('keydown.ui-page-image', function (evt){
				switch(evt.which){
					case 37:
						$template.imageViewer('previous');
						break;
					case 39:
						$template.imageViewer('next');
						break;
				}
			});
			
		},
		
		deleteView: function(){
			this.$template.imageViewer('destroy');
			$(document).off('keydown.ui-page-image');
		}
	};
}));