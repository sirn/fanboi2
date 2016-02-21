var gulp              = require('gulp');
var sourcemaps        = require('gulp-sourcemaps');
var concat            = require('gulp-concat');
var es                = require('event-stream');

var sass              = require('gulp-sass');
var postcss           = require('gulp-postcss');

var uglify            = require('gulp-uglify');
var source            = require('vinyl-source-stream');
var buffer            = require('vinyl-buffer');
var browserify        = require('browserify');
var tsify             = require('tsify');


/* Settings
 * ---------------------------------------------------------------------- */

var paths = {

    /* Path for storing application-specific assets. */
    app: {
        assets: 'assets/app/assets/*',
        stylesheets: [
            'assets/app/stylesheets/app.scss',
            'assets/app/stylesheets/*.scss',
            'assets/app/stylesheets/themes/*.scss'
        ],
        javascripts: {
            glob: 'assets/app/javascripts/**/*.ts',
            base: 'assets/app/javascripts/',
            typings: 'typings/browser.d.ts',
            entry: 'assets/app/javascripts/app.ts'
        }
    },

    /* Path for storing third-party assets. */
    vendor: {
        assets: 'assets/vendor/assets/*',
        stylesheets: 'assets/vendor/stylesheets/**/*.css',
        javascripts: [
            'assets/vendor/javascripts/**/*.js'
        ]
    },

    /* Path for storing compatibility assets. */
    legacy: {
        assets: 'assets/legacy/assets/*',
        stylesheets: 'assets/legacy/stylesheets/**/*.css',
        javascripts: 'assets/legacy/javascripts/**/*.js'
    },

    /* Path to output compiled assets to. */
    dest: 'fanboi2/static'
};


/* Assets
 * ---------------------------------------------------------------------- */

gulp.task('assets', function(){
    return es.merge([
            gulp.src(paths.app.assets),
            gulp.src(paths.vendor.assets),
            gulp.src(paths.legacy.assets)]).
        pipe(gulp.dest(paths.dest));
});


/* Stylesheets
 * ---------------------------------------------------------------------- */

var postcssProcessors = [
    require('autoprefixer'),
    require('postcss-round-subpixels'),
    require('css-mqpacker'),
    require('postcss-urlrev')({
        relativePath: paths.dest,
        replacer: function(url, hash) {
            /* PostCSS-Urlrev uses ?v= by default. Override to
             * make it compatible with ?h= syntax in app. */
            return url + '?h=' + hash.slice(0, 8);
        }
    }),
    require('csswring')
];

gulp.task('styles/app', ['assets'], function(){
    return gulp.
        src(paths.app.stylesheets).
        pipe(sourcemaps.init()).
            pipe(sass().on('error', sass.logError)).
            pipe(concat('app.css')).
            pipe(postcss(postcssProcessors)).
        pipe(sourcemaps.write('.')).
        pipe(gulp.dest(paths.dest));
});

gulp.task('styles/vendor', function(){
    return gulp.
        src(paths.vendor.stylesheets).
        pipe(sourcemaps.init()).
            pipe(concat('vendor.css')).
            pipe(postcss(postcssProcessors)).
        pipe(sourcemaps.write('.')).
        pipe(gulp.dest(paths.dest));
});

gulp.task('styles', [
    'styles/app',
    'styles/vendor'
]);


/* JavaScripts
 * ---------------------------------------------------------------------- */

var externalDependencies = [
    'dom4',
    'domready',
    'es6-promise',
    'virtual-dom',
    'whatwg-fetch'
];

gulp.task('javascripts/app', function(){
    return browserify({debug: true}).
        plugin(tsify).
        require(paths.app.javascripts.typings, {entry: true}).
        require(paths.app.javascripts.entry, {entry: true}).
        external(externalDependencies).
        bundle().
            on('error', function(err) {
                console.log(err.message);
                this.emit('end');
            }).
            pipe(source('app.js')).
            pipe(buffer()).
            pipe(sourcemaps.init({loadMaps: true})).
                pipe(uglify()).
            pipe(sourcemaps.write('.')).
            pipe(gulp.dest(paths.dest));
});

gulp.task('javascripts/vendor', function(){
    return browserify({debug: true}).
        require(externalDependencies).
        bundle().
            on('error', function(err) {
                console.log(err.message);
                this.emit('end');
            }).
            pipe(source('vendor.js')).
            pipe(buffer()).
            pipe(sourcemaps.init({loadMaps: true})).
                pipe(uglify()).
            pipe(sourcemaps.write('.')).
            pipe(gulp.dest(paths.dest));
});

gulp.task('javascripts/legacy', function(){
    return gulp.
        src(paths.legacy.javascripts).
        pipe(sourcemaps.init()).
            pipe(concat('legacy.js')).
            pipe(uglify()).
        pipe(sourcemaps.write('.')).
        pipe(gulp.dest(paths.dest));
});

gulp.task('javascripts', [
    'javascripts/app',
    'javascripts/vendor',
    'javascripts/legacy'
]);


/* Defaults
 * ---------------------------------------------------------------------- */

gulp.task('default', ['assets', 'styles', 'javascripts']);

gulp.task('watch', ['default'], function(){
    gulp.watch(paths.app.stylesheets, ['styles/app']);
    gulp.watch(paths.vendor.stylesheets, ['styles/vendor']);

    gulp.watch(paths.app.javascripts.glob, ['javascripts/app']);
    gulp.watch(paths.vendor.javascripts, ['javascripts/vendor']);
    gulp.watch(paths.legacy.javascripts, ['javascripts/legacy']);
});
