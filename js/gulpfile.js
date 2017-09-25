
var gulp = require('gulp');
var concat = require('gulp-concat');
var rename = require('gulp-rename');
var uglify = require('gulp-uglify');


// Path
var source = './src'; // dossier de travail
var dest = '.'; // dossier à livrer

var files = ["utils.js", "node.js", "event.js", "deferred.js", "api.js", "file.js", "table.js", "app.js", "device.js", "arbo.js", "rules.js", "devices/*.js"];

files = files.map(function(srcFile){
	return source + '/' + srcFile;
})

gulp.task('build', function () {
  return gulp.src(files)
    .pipe(concat('ething.js'))
	.pipe(gulp.dest(dest))
    .pipe(rename({
		suffix: '.min'
	}))
    .pipe(uglify())
    .pipe(gulp.dest(dest));
});


// Tâche par défaut
gulp.task('default', ['build']);
