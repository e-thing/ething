(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','./core','css!./droppable'], factory);
    }
}(this, function ($, UI) {
	
	// The plugin code (ie: http://stackoverflow.com/questions/10253663/how-to-detect-the-dragleave-event-in-firefox-when-dragging-outside-the-window/10310815#10310815)
	$.fn.draghover = function(options) {
	  return this.each(function() {

		var collection = $(),
			self = $(this);

		self.on('dragenter', function(e) {
		  if (collection.length === 0) {
			self.trigger('draghoverstart');
		  }
		  collection = collection.add(e.target);
		});

		self.on('dragleave drop', function(e) {
		  collection = collection.not(e.target);
		  if (collection.length === 0) {
			self.trigger('draghoverend');
		  }
		});
	  });
	};
	
	function traverseFileTree(item, path, cb) {
	  path = path || "";
	  if (item.isFile) {
		// Get file
		item.file(function(file) {
			if(typeof cb === 'function') cb(file, path);
		});
	  } else if (item.isDirectory) {
		// Get folder contents
		var dirReader = item.createReader();
		dirReader.readEntries(function(entries) {
		  for (var i=0; i<entries.length; i++) {
			traverseFileTree(entries[i], path + item.name + "/", cb);
		  }
		});
	  }
	}
	
	
	var Droppable = function(options){
		
		this.options = $.extend(true,{
			onDrop: null,
			target: 'body',
			text: 'Drop Here'
		}, options);
		
		this.enable();
	}
	
	Droppable.prototype.enable = function(){
		
		var self = this,
			$target = $(this.options.target),
			$overlay = $('<div class="drop-overlay"><span>'+this.options.text+'</span></div>');
		
		$target.draghover().on({
		  'draghoverstart': function() {
			$overlay.appendTo($target);
			if(['relative','absolute','fixed'].indexOf($target.css('position'))===-1)
				$target.addClass('drop-overlay-ctnr');
		  },
		  'draghoverend': function() {
			$overlay.detach();
			$target.removeClass('drop-overlay-ctnr');
		  }
		});
		$target.on('dragenter', function(e) {
			e.preventDefault();
			e.stopPropagation();
			return false;
		});
		
		$target.on('dragover', function(e) {
			e.preventDefault(); // Cancel drop forbidding
			e.stopPropagation();
			return false;
		});
		
		$target.on('dragleave', function(e) {
			e.preventDefault();
			e.stopPropagation();
			return false;
		});
		
		$target.on('drop', function(e) {
			
			if(e.originalEvent.dataTransfer && e.originalEvent.dataTransfer.files.length){
				// Stop the propagation of the event
				e.preventDefault();
				e.stopPropagation();
				
				// fetch FileList object
				var files = e.originalEvent.dataTransfer.files;

			   // process all File objects
				for (var i = 0, f; f = files[i]; i++) {
					
					// folder ?
					var item = e.originalEvent.dataTransfer.items[i];
					if(item.webkitGetAsEntry){
						var entry = item.webkitGetAsEntry();
						if (entry) {
							traverseFileTree(entry, '', function(file,path){
								if(typeof self.options.onDrop == 'function')
									self.options.onDrop(file,path);
							});
						}
					} else {
						if(typeof self.options.onDrop == 'function')
							self.options.onDrop(f, '');
					}
				} 
			}
			else {
				alert('unable to drop this file');
			}
			return false;
		});
		
	};
	
	Droppable.prototype.disable = function(){
		var $target = $(this.options.target);
		
		$target.removeClass('drop-overlay-ctnr');
		$target.children('.drop-overlay').remove();
		$target.off('dragenter');
		$target.off('dragover');
		$target.off('dragleave');
		$target.off('drop');
		$target.off('draghoverstart');
		$target.off('draghoverend');
		
	};
	
	
	
	
	UI.Droppable = Droppable;
	
	
	return Droppable;
}));