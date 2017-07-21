
var ok = true;

var modules = ['vm','fs','url','./../lib/core.js'];

function checkModule(moduleName){
	try {
		require.resolve(moduleName);
	} catch(e) {
		console.error("module '"+moduleName+"' is not found");
		return false;
	}
	return true;
}


modules.forEach(function(m){
	if(!checkModule(m)) ok = false;
});




process.exit(ok ? 0 : 1);
