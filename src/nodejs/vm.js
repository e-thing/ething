

function usage(){
	console.error();
	console.error("usage:");
	console.error("  "+process.argv.slice(0,2).join(' ')+" [--stdout file] [--stderr file] [--result file]");
	console.error("      [--globals json] [-t timeout] [--user user] [--password password] [--apiUrl url] script");
	console.error();
}

function extend(a, b){
	for(var i in b){
		if(typeof b[i] !== 'undefined' && b[i] !== null) a[i] = b[i];
	}
	return a;
}


var scriptFile = null;
var stdoutFile = './stdout.log';
var stderrFile = './stderr.log';
var resultFile = './result';
var globals = {};
var timeout = 300000;
var user = 'ething';
var password = 'admin';
var apiUrl = 'http://localhost/ething/api';

// arguments

var arguments = process.argv.slice(2);
if(!arguments.length){
	usage();
	process.exit(1);
}

while(arguments.length){
	switch (arguments[0]) {
		case '--result':
			arguments.shift();
			if(!arguments.length){
				usage();
				process.exit(1);
			}
			resultFile = arguments[0];
			break;
		case '--stdout':
			arguments.shift();
			if(!arguments.length){
				usage();
				process.exit(1);
			}
			stdoutFile = arguments[0];
			break;
		case '--stderr':
			arguments.shift();
			if(!arguments.length){
				usage();
				process.exit(1);
			}
			stderrFile = arguments[0];
			break;
		case '--globals':
			arguments.shift();
			if(!arguments.length){
				usage();
				process.exit(1);
			}
			try {
				extend(globals,JSON.parse(arguments[0]));
			} catch(e){
				console.error("invalid JSON object given for the --globals argument");
				process.exit(1);
			}
			break;
		case '-t':
			arguments.shift();
			if(!arguments.length){
				usage();
				process.exit(1);
			}
			timeout = parseInt(arguments[0]);
			break;
		case '--user':
			arguments.shift();
			if(!arguments.length){
				usage();
				process.exit(1);
			}
			user = arguments[0];
			break;
		case '--password':
			arguments.shift();
			if(!arguments.length){
				usage();
				process.exit(1);
			}
			password = arguments[0];
			break;
		case '--apiUrl':
			arguments.shift();
			if(!arguments.length){
				usage();
				process.exit(1);
			}
			
			// parse url
			var url = require('url');
			var tmpurl = extend(url.parse('http://localhost'), url.parse(arguments[0]));
			tmpurl.pathname = tmpurl.pathname.replace(/\/?$/,'/api');
			apiUrl = url.format(tmpurl);
			
			break;
		default:
			if(scriptFile===null){
				scriptFile = arguments[0];
			}
			break;
	}
	arguments.shift();
}

if(scriptFile===null){
	usage();
	process.exit(1);
}

var fs = require('fs');
if (!fs.existsSync(scriptFile)) {
    console.error("unable to read the file "+scriptFile);
	process.exit(1);
}

var script = fs.readFileSync(scriptFile).toString('utf8');


var EThing = require("./../../js/ething.js").EThing;



EThing.initialize({
  apiUrl: apiUrl,
  login: user,
  password: password
}, function(){
	
	const vm = require('vm');
	const output = stdoutFile==='-' ? process.stdout : fs.createWriteStream(stdoutFile);
	const errorOutput = stderrFile==='-' ? process.stderr : fs.createWriteStream(stderrFile);
	const resultOutput = resultFile==='-' ? process.stdout : fs.createWriteStream(resultFile);
	const logger = new console.Console(output, errorOutput);
	
	extend(globals, {
		EThing: EThing,
		console: logger,
		Buffer: Buffer,
		setTimeout: setTimeout,
		clearTimeout: clearTimeout,
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
	});
	
	try {
		
		var options = {
			displayErrors  : true
		};
		
		if(timeout>0) options.timeout = timeout;
		
		var result = vm.runInNewContext(script, globals, options);
		
		if(typeof result != 'undefined' && result !== null){
			resultOutput.write(JSON.stringify(result, null, ' '));
		}
		
	} catch(e){
		logger.error(e);
	}
	
}, function(error) {
// on error
  console.error(error.message);
  process.exit(1);
});



