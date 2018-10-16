var EThing = require('./ething.js');

function usage(){
	console.error();
	console.error("usage:");
	console.error("  "+process.argv.slice(0,2).join(' ')+" [--out file]");
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
var outFile = './out.log';
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
		case '--out':
			arguments.shift();
			if(!arguments.length){
				usage();
				process.exit(1);
			}
			outFile = arguments[0];
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
				console.error("invalid JSON object given for the --globals argument: ", e);
                console.log(arguments[0])
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



	
if(verbose) console.log('script stdout:',outFile);

const vm = require('vm');


function _exit(code) {
    outStream.end(() => {
        outStream.isOpen = false
        process.exit(code);
    })
}

var stream = require('stream');

var outStream = outFile==='-' ? process.stdout : fs.createWriteStream(outFile);
outStream.isOpen = true

var stdoutStream = new stream.Writable();

stdoutStream._write = function (chunk, encoding, done) {
    if (outStream.isOpen) {
        outStream.write(JSON.stringify({
            type: 'stdout',
            chunk: chunk.toString()
        })+",\n", done);
    }
};

var stderrStream = new stream.Writable();

stderrStream._write = function (chunk, encoding, done) {
    if (outStream.isOpen) {
        outStream.write(JSON.stringify({
            type: 'stderr',
            chunk: chunk.toString()
        })+",\n", done);
    }
};

const logger = new console.Console(stdoutStream, stderrStream);

process.on('uncaughtException', function(err){
	if(verbose) console.error('Error in script:', err);
	logger.error(err);
	_exit(1);
});

process.on('unhandledRejection', err => {
	if(verbose) console.error('Error in script:', err);
	logger.error(err);
	_exit(1);
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
	
	
} catch(e){
	if(verbose) console.error('Error in script:', e);
	logger.error(e);
    _exit(1);
}

