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
			"meta/App","meta/BLEAEthernetGateway","meta/BLEAGateway","meta/BLEALocalGateway","meta/Denon","meta/Device","meta/File","meta/Http","meta/Light","meta/MQTT","meta/Miflora","meta/MihomeDevice","meta/MihomeGateway","meta/MihomeSensorHT","meta/MySensorsEthernetGateway","meta/MySensorsGateway","meta/MySensorsNode","meta/MySensorsSensor","meta/MySensorsSerialGateway","meta/RFLinkGateway","meta/RFLinkNode","meta/RFLinkSerialGateway","meta/RTSP","meta/Resource","meta/SSH","meta/Switch","meta/Table","meta/Thermometer","meta/YeelightBulbRGBW","meta/ZigateGateway","meta/ZigateSerialGateway","widget/generic/button","widget/generic/chart","widget/generic/clock","widget/generic/gauge","widget/generic/image","widget/generic/label","widget/generic/slider","widget/generic/stream","widget/generic/video","widget/resource/Denon","widget/resource/GenericLight","widget/resource/GenericNumber","widget/resource/GenericRGBW","widget/resource/GenericSwitch","widget/resource/GenericWeather","widget/resource/Light","widget/resource/RTSP","widget/resource/Thermometer","widget/resource/YeelightBulbRGBW"
		],
		exclude: ['ething', 'form', 'jquery.gridster', 'table', 'circleBar', 'csv', 'imageviewer', 'plot', 'tree']
	}],
	
	removeCombined: true,
	
	mainConfigFile: './src/main.js'
})