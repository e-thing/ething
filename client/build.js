({
	appDir: "./src",
	
	baseUrl: "lib",
	
	dir: "./build",
	
	//optimize: "none",
	
	modules: [
	{
		name: '../main',
		include: [
			'require-text',
			'require-json',
			'ui/resourceselect',
			'ui/tablefieldselect',
			'ui/devicerequest',
			'ui/deviceoperationselect',
			'ui/datasource',
			'ui',
			'ui/container',
			'ui/droppable',
			'ui/header',
			'ui/infopanel',
			'ui/notification',
			'ui/uploader',
			'ui/modal',
			'ui/browser',
			'ui/savedialog',
			'ui/opendialog',
			'ui/formmodal',
			'ui/textviewer'
		],
		exclude: ['ething', 'json!config.json']
	}
	],
	
	removeCombined: true,
	
	mainConfigFile: './src/main.js'
})