const express = require('express');
const bodyParser = require('body-parser');
const vm = require('vm');
const Writable = require('stream').Writable;
var EThing = require("./../../js/ething.js").EThing;

const app = express();


var serverPort = 3000;

var textBodyParser = bodyParser.text();

app.post('/run', textBodyParser, function (req, res) {
	
	execute(req.body, {
		stdout : function(chunk, encoding){
			console.log('stdout: '+chunk);
			if(!res.finished) res.write(chunk, encoding);
		},
		stderr : function(chunk, encoding){
			console.log('stderr: '+chunk);
			if(!res.finished) res.write(chunk, encoding);
		},
		end: function(result){
			console.log('result: '+result);
			res.end();
		}
	});
	
	//res.send('Hello World!');
});


function extend(a, b){
	for(var i in b){
		if(typeof b[i] !== 'undefined' && b[i] !== null) a[i] = b[i];
	}
	return a;
}

class CallbackWriter extends Writable {
    constructor(options) {
        super(options);
        this._cb = (options || {}).callback || null;
    }

    _write(chunk, encoding, callback) {
        if(typeof this._cb === 'function') this._cb(chunk, encoding);
        callback();
    }
}

function toStream(std){
	if(typeof std === 'string'){
		// store in file
		return fs.createWriteStream(std);
	} else if(typeof std === 'function') {
		return new CallbackWriter({
			callback: std
		});
	} else if(std instanceof Writable){
		return std;
	} else {
		return null;
	}
}

var uncaughtExceptionListeners = [];

function addUncaughtExceptionListener(cb){
	uncaughtExceptionListeners.push(cb);
}

function removeUncaughtExceptionListener(cb){
	for(var i in uncaughtExceptionListeners){
		if(uncaughtExceptionListeners[i] === cb){
			uncaughtExceptionListeners.splice(i, 1);
		}
	}
}

process.on('uncaughtException', function(err){
	
	if(uncaughtExceptionListeners.length === 0){
		console.error(err);
		process.exit(1);
		return;
	}
	
	for(var i in uncaughtExceptionListeners){
		if(uncaughtExceptionListeners[i] === cb){
			uncaughtExceptionListeners[i](err);
		}
	}
	
	
});


const { fork } = require('child_process');
var execute = function(script, options){
	
	console.log('start '+new Date().toISOString());
	
	const forked = fork('client.js');
	
	console.log('after forking '+new Date().toISOString());
	
	forked.on('close', function(){
		console.log('client closed');
	});
	
	forked.on('error', function(){
		console.log('client error');
	});
	
	forked.on('exit', function(){
		console.log('client exited');
	});
	
	console.log('end');
}

var execute2 = function(script, options){
	
	options = extend({
		timeout: 0,
		stdout: null,
		stderr: null,
		global: {},
		end: null
	}, options || {});
	
	const logger = new console.Console(toStream(options.stdout), toStream(options.stderr));
	
	var uncaughtException = function(err){
		console.error('Error in script:', err);
		/*logger.error(err);*/
		
		if(typeof options.end === 'function'){
			options.end(null);
		}
		
		removeUncaughtExceptionListener(uncaughtException);
	};
	
	addUncaughtExceptionListener(uncaughtException);
	
	var globals = extend({}, options.global);
	
	var globals = extend(globals, {
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
	
	removeUncaughtExceptionListener(uncaughtException);
	
}




/*EThing.initialize({
  apiUrl: 'http://localhost/ething/api',
  login: 'ething',
  password: 'admin'
}, function(){
	
	console.log('EThing initialized');

	app.listen(serverPort, function () {
	  console.log('listening on port '+serverPort);
	});
	
});*/



execute('', {});