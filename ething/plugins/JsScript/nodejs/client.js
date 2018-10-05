
console.log('in client '+new Date().toISOString());

var EThing = require("./../../js/ething.min.js").EThing;
const vm = require('vm');

var script = 'setTimeout(function(){console.log("hello world !");}, 1000)';

EThing.config.apiUrl = 'http://localhost/ething/api';

EThing.auth.setBasicAuth('ething', 'admin');

var options = {
	timeout: 0,
	stdout: null,
	stderr: null,
	global: {},
	end: null
};

const logger = new console.Console(process.stdout, process.stdout);





var globals = {
	EThing: EThing,
	console: logger,
	Buffer: Buffer,
	setTimeout: setTimeout,
	setInterval: setInterval,
	clearTimeout: clearTimeout,
	clearInterval: clearInterval,
	ArrayBuffer: ArrayBuffer,
	Int8Array: Int8Array,
	Uint8Array: Uint8Array,
	Uint8ClampedArray: Uint8ClampedArray,
	Int16Array: Int16Array,
	Uint16Array: Uint16Array,
	Int32Array: Int32Array,
	Uint32Array: Uint32Array,
	Float32Array: Float32Array,
	Float64Array: Float64Array,
	DataView: DataView
};

try {
	
	var vmOptions = {
		displayErrors  : true,
		filename : 'script.js'
	};
	
	if(options.timeout>0){
		vmOptions.timeout = options.timeout;
		console.log('script timeout:', vmOptions.timeout,'ms');
	}
	
	console.log('start script', new Date().toISOString());
	
	var result = vm.runInNewContext(script, globals, vmOptions);
	
	console.log('end script', new Date().toISOString());
	
	console.log(typeof options.end);
	if(typeof options.end === 'function'){
		options.end(result);
	}
	
} catch(e){
	console.error('Error in script:', e);
	logger.error(e);
	if(typeof options.end === 'function'){
		options.end(null);
	}
}