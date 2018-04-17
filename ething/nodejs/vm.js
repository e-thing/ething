

function usage(){
	console.error();
	console.error("usage:");
	console.error("  "+process.argv.slice(0,2).join(' ')+" [--stdout file] [--stderr file] [--result file]");
	console.error("      [--globals json] [-t timeout] [--user user] [--password password] [--serverUrl url]");
	console.error("      [--apikey key] [--filename name] script");
	console.error();
}

function extend(a, b){
	for(var i in b){
		if(typeof b[i] !== 'undefined' && b[i] !== null) a[i] = b[i];
	}
	return a;
}

var filename = null;
var scriptFile = null;
var stdoutFile = './stdout.log';
var stderrFile = './stderr.log';
var resultFile = './result';
var globals = {};
var timeout = 300000; // in ms
var user = 'ething';
var password = null;
var apiKey = null;
var serverUrl = 'http://localhost:8000';
var verbose = false;

// arguments

var arguments = process.argv.slice(2);
if(!arguments.length){
	usage();
	process.exit(1);
}

while(arguments.length){
	
	switch (arguments[0]) {
		case '--verbose':
			verbose = true;
			break;
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
		case '--filename': // used for stack trace
			arguments.shift();
			if(!arguments.length){
				usage();
				process.exit(1);
			}
			filename = arguments[0];
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
		case '--apikey':
			arguments.shift();
			if(!arguments.length){
				usage();
				process.exit(1);
			}
			apiKey = arguments[0];
			break;
		case '--serverUrl':
			arguments.shift();
			if(!arguments.length){
				usage();
				process.exit(1);
			}
			
			// parse url
			var url = require('url');
			var tmpurl = extend(url.parse(serverUrl), url.parse(arguments[0]));
			tmpurl.pathname = tmpurl.pathname.replace(/\/?$/,'/api');
			serverUrl = url.format(tmpurl);
			
			break;
		default:
			if(scriptFile===null){
				scriptFile = arguments[0];
			} else {
				console.error('invalid argument',arguments[0]);
				usage();
				process.exit(1);
			}
			break;
	}
	arguments.shift();
}



if(verbose){
	console.log('command:',process.argv.join(' '));
	console.log('serverUrl:',serverUrl);
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

if(verbose) console.log('script file:',scriptFile);

var EThing = require("./../webui/node_modules/ething-js");


if(!filename){
	filename = scriptFile.split('/').reverse()[0];
}


if(serverUrl)
	EThing.config.serverUrl = serverUrl;

if(apiKey)
	EThing.auth.setApiKey(apiKey);
else if(user && password)
	EThing.auth.setBasicAuth(user, password);



function isResource(json){
	return json.hasOwnProperty('id') && json.hasOwnProperty('type') && json.hasOwnProperty('name');
}

for(var k in globals){
    if(isResource(globals[k])){
        try{
            globals[k] = EThing.instanciate(globals[k]);
        } catch(e){}
    }
}



	
if(verbose) console.log('script stdout:',stdoutFile);
if(verbose) console.log('script stderr:',stderrFile);
if(verbose) console.log('script result:',resultFile);

const vm = require('vm');
const output = stdoutFile==='-' ? process.stdout : fs.createWriteStream(stdoutFile);
const errorOutput = stderrFile==='-' ? process.stderr : fs.createWriteStream(stderrFile);
const resultOutput = resultFile==='-' ? process.stdout : fs.createWriteStream(resultFile);
const logger = new console.Console(output, errorOutput);

process.on('uncaughtException', function(err){
	if(verbose) console.error('Error in script:', err);
	logger.error(err);
	process.exit(1);
});

extend(globals, {
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
});

try {
	
	var options = {
		displayErrors  : true,
		filename : filename
	};
	
	if(timeout>0){
		options.timeout = timeout;
		if(verbose) console.log('script timeout:', options.timeout,'ms');
	}
	
	if(verbose) console.log('start script', new Date().toISOString());
	
	var result = vm.runInNewContext(script, globals, options);
	
	if(verbose) console.log('end script', new Date().toISOString());
	
	if(typeof result != 'undefined' && result !== null){
		try {
			var resultStr = JSON.stringify(result, null, ' ');
			resultOutput.write(resultStr);
		} catch(e){
			if(verbose) console.error('Error stringify output:', e);
		}
	}
	
} catch(e){
	if(verbose) console.error('Error in script:', e);
	logger.error(e);
}
	
	

