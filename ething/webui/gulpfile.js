
var gulp = require('gulp');
var filelist = require('gulp-filelist');
var fs = require("fs");
var del = require('del');


// Path
var source = './src';
var build = './dist';

var dyn_folders = ['meta', 'widget/generic', 'widget/resource'];


gulp.task('clean', function (done) {
	
	del.sync(build, {force:true});
	
	done();
	
});

gulp.task('list', function (done) {
	
	dyn_folders.forEach(function(folder){
		
		var dir = source+'/'+folder;
		
		gulp
			.src('*.js', {cwd: dir})
			.pipe(filelist('list.json', { removeExtensions: true }))
			.pipe(gulp.dest(dir))
		
	});
	
	done();
	
});

gulp.task('configure', function (done) {
	
	var includes = [];
	
	dyn_folders.forEach(function(folder){
		var dir = source+'/'+folder;
		var contents = fs.readFileSync(dir+"/list.json");
		var filenames = JSON.parse(contents);
		
		includes = includes.concat(filenames.map(function(filename){
			return folder + '/' + filename;
		}));
		
	});
	
	var str = includes.map(function(i){
		return '"' + i + '"';
	}).join(',');
	
	console.log(includes);
	
	var build_contents = fs.readFileSync("build_tmpl.js", 'utf8');
	fs.writeFileSync("build.js", build_contents.replace('//INCLUDE//', str) );
	
	done();
});


gulp.task('build', function (cb) {
	
	var rjs = require("requirejs");
	var fs = require('fs');
	var path = require('path');
	
	
	var config_contents = fs.readFileSync("build.js", 'utf8');
	
	var config = eval(config_contents);
	
	console.log(config);
	
	rjs.optimize(config, function(buildResponse){
		
		// remove bundled files
		
		var state = 'new';
		var re_css = /^.*css!/;
		var re_text = /^.*text!/;
		var buildFile = null;
		buildResponse.split(/\r?\n/).forEach(function(line){
			
			if(line==''){
				state = 'new';
			} else if(/^\-+$/.test(line)){
				state = 'dep';
			} else {
				var file = line;
				
				if(re_css.test(file))
					file = file.replace(re_css, '') + '.css';
				if(re_text.test(file))
					file = file.replace(re_text, '');
				
				if(state == 'new'){
					buildFile = file;
				} else {
					if(buildFile != file){
						
						var absfile = path.join(config.dir,file);
						
						// remove file
						if (fs.existsSync(absfile)) {
							console.log('removing', absfile)
							fs.unlinkSync(absfile);
						}
						
					}
				}
				
				//console.log(state, file, line)
				
			}
			
		})
		
		
		cb();
	});
	
	
	
});


// Tâche par défaut
gulp.task('default', ['clean', 'list', 'configure', 'build']);
