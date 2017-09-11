
var gulp = require('gulp');
var concat = require('gulp-concat');
var rename = require('gulp-rename');
var uglify = require('gulp-uglify');


// Path
var source = './src'; // dossier de travail
var dest = '.'; // dossier à livrer

gulp.task('build', function () {
  return gulp.src([source+"/utils.js", source+"/node.js", source+"/event.js", source+"/deferred.js", source+"/api.js", source+"/arbo.js", source+"/rules.js"])
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
