({
	appDir: "./src",
	
	baseUrl: "lib",
	
	dir: "./dist",
	
	optimize: "none",//"uglify",
	
	modules: [{
		name: '../main',
		include: [
			'ui/formmodal',
			'ui/browser',
			'ui/container',
			'ui/datasource',
			'ui/devicerequest',
			'ui/droppable',
			'ui/gridwidget',
			'ui/header',
			'ui/http',
			'ui/infopanel',
			'ui/localipselect',
			'ui/notification',
			'ui/opendialog',
			'ui/resourcedataselect',
			'ui/resourceselect',
			'ui/savedialog',
			'ui/tablefieldselect',
			'ui/tableviewer',
			'ui/textviewer',
			'ui/uploader',
			'ui/widget',
			'css!ui/default',
			//INCLUDE//
		],
		exclude: ['ething', 'form', 'jquery.gridster', 'table', 'circleBar', 'csv', 'imageviewer', 'plot', 'tree']
	}],
	
	removeCombined: true,
	
	mainConfigFile: './src/main.js'
})