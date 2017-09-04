(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['js/ui', 'jquery', 'ething', 'https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.17/d3.min.js', 'css!./tree'], factory);
    }
}(this, function (UI, $, EThing, d3) {
	
	
	function makeTree(root){
				
		function getChildren(resource){
			return EThing.arbo.find(function(r){
				var createdBy = r.createdBy();
				return createdBy && createdBy.id === resource.id();
			});
		}
		
		function hasParent(resource){
			return !!resource.createdBy();
		}
		
		var level = 0;
		
		function createNode(resource){
			return {
				name: resource.name(),
				resource: resource,
				children: [],
				active: true,
				level: level
			};
		}
		
		function add(parentItem, resource){
			var item = createNode(resource);
			
			item.parent = parentItem.resource;
			
			level++;
			getChildren(resource).forEach(function(r){
				add(item, r);
			});
			level--;
			
			if(item.active || item.children.length){
				
				if(!item.children.length)
					delete item.children;
				
				parentItem.children.push(item);
			}
			
			return item;
		}
		
		
		var rootNode;
		
		if(root instanceof EThing.Resource){
			
			rootNode = createNode(root);
			
			getChildren(root).forEach(function(r){
				add(rootNode, r); // recursive
			});
			
		} else {
			rootNode = {
				name: 'EThing',
				resource: null,
				children: []
			};
			
			EThing.arbo.find(function(r){
				return !(r instanceof EThing.Folder);
			}).forEach(function(r){
				if(!hasParent(r)){
					add(rootNode, r); // recursive
				}
			});
		}
		
		return rootNode;
	}
	
	
	//---------
	
	
	
	var Tree = function(element, opt){
		
		var $element = $(element).addClass('tree');
		
		this.options = $.extend({
			root: null,
			height: null,
			width: null
		}, opt);
		
		var self = this;
		
		var margin = {top: 10, right: 120, bottom: 10, left: 100},
			width = (this.options.width || 960) - margin.right - margin.left,
			height = (this.options.height || 800) - margin.top - margin.bottom;

		var i = 0,
			duration = 750,
			root;

		var tree = d3.layout.tree()
			.size([height, width]);

		var diagonal = d3.svg.diagonal()
			.projection(function(d) { return [d.y, d.x]; });

		var svg = d3.select($element[0]).append("svg")
			.attr("width", width + margin.right + margin.left)
			.attr("height", height + margin.top + margin.bottom)
		  .append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
		
		setTimeout(function(){
			
			root = makeTree(self.options.root || null);
			root.x0 = height / 2;
			root.y0 = 0;

			function collapse(d) {
				if (d.children) {
					d._children = d.children;
					d._children.forEach(collapse);
					d.children = null;
				}
			}

			//root.children.forEach(collapse);
			update(root);
			
		},1);

		d3.select(self.frameElement).style("height", "800px");

		function update(source) {

		  // Compute the new tree layout.
		  var nodes = tree.nodes(root).reverse(),
			  links = tree.links(nodes);

		  // Normalize for fixed-depth.
		  nodes.forEach(function(d) { d.y = d.depth * 180; });

		  // Update the nodes…
		  var node = svg.selectAll("g.node")
			  .data(nodes, function(d) { return d.id || (d.id = ++i); });

		  // Enter any new nodes at the parent's previous position.
		  var nodeEnter = node.enter().append("g")
			  .attr("class", function(d) {
				  return d.resource ? "node node-"+d.resource.baseType() : "node";
			   })
			  .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; });

		  nodeEnter.append("circle")
			  .attr("r", 1e-6)
			  .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; })
			  .on("click", click);

		  nodeEnter.append("text")
			  .attr("x", function(d) { return d.children || d._children ? -10 : 10; })
			  .attr("dy", ".35em")
			  .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
			  .text(function(d) { return d.name; })
			  .style("fill-opacity", 1e-6)
			  .on("click", open);

		  // Transition nodes to their new position.
		  var nodeUpdate = node.transition()
			  .duration(duration)
			  .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

		  nodeUpdate.select("circle")
			  .attr("r", 4.5)
			  .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

		  nodeUpdate.select("text")
			  .style("fill-opacity", 1);

		  // Transition exiting nodes to the parent's new position.
		  var nodeExit = node.exit().transition()
			  .duration(duration)
			  .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
			  .remove();

		  nodeExit.select("circle")
			  .attr("r", 1e-6);

		  nodeExit.select("text")
			  .style("fill-opacity", 1e-6);

		  // Update the links…
		  var link = svg.selectAll("path.link")
			  .data(links, function(d) { return d.target.id; });

		  // Enter any new links at the parent's previous position.
		  link.enter().insert("path", "g")
			  .attr("class", "link")
			  .attr("d", function(d) {
				var o = {x: source.x0, y: source.y0};
				return diagonal({source: o, target: o});
			  });

		  // Transition links to their new position.
		  link.transition()
			  .duration(duration)
			  .attr("d", diagonal);

		  // Transition exiting nodes to the parent's new position.
		  link.exit().transition()
			  .duration(duration)
			  .attr("d", function(d) {
				var o = {x: source.x, y: source.y};
				return diagonal({source: o, target: o});
			  })
			  .remove();

		  // Stash the old positions for transition.
		  nodes.forEach(function(d) {
			d.x0 = d.x;
			d.y0 = d.y;
		  });
		}

		// Toggle children on click.
		function click(d) {
		  if (d.children) {
			d._children = d.children;
			d.children = null;
		  } else {
			d.children = d._children;
			d._children = null;
		  }
		  update(d);
		}
		
		// open resource on click
		function open(d) {
			if(d.resource && !UI.open(d.resource))
				alert('Unable to open this resource !');
		}
		
	}
	
	
	
	return Tree;
}));