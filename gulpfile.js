var gulp = require("gulp");
var sourcemaps = require("gulp-sourcemaps");
var concat = require("gulp-concat");
var es = require("event-stream");

var sass = require("gulp-sass");
var postcss = require("gulp-postcss");

var uglify = require("gulp-uglify");
var source = require("vinyl-source-stream");
var buffer = require("vinyl-buffer");
var browserify = require("browserify");
var tsify = require("tsify");

/* Utils
 * -------------------------------------------------------------------------------- */

function logError(error) {
    console.log(error);
    this.emit("end");
}

/* Assets
 * -------------------------------------------------------------------------------- */

function assets() {
    return es
        .merge([
            gulp.src("assets/admin/assets/*"),
            gulp.src("assets/app/assets/*"),
            gulp.src("assets/legacy/assets/*"),
            gulp.src("assets/vendor/assets/*")
        ])
        .pipe(gulp.dest("fanboi2/static"));
}

/* Styles
 * -------------------------------------------------------------------------------- */

var postcssProcessors = [
    require("autoprefixer"),
    require("postcss-round-subpixels"),
    require("css-mqpacker"),
    require("postcss-urlrev")({
        relativePath: "fanboi2/static",
        replacer: function(url, hash) {
            /* PostCSS-Urlrev uses ?v= by default. Override to
             * make it compatible with ?h= syntax in app. */
            return url + "?h=" + hash.slice(0, 8);
        }
    }),
    require("cssnano")({ preset: "default" })
];

function styleApp() {
    return gulp
        .src([
            "assets/app/stylesheets/app.scss",
            "assets/app/stylesheets/*.scss",
            "assets/app/stylesheets/themes/*.scss"
        ])
        .pipe(sourcemaps.init())
        .pipe(sass().on("error", sass.logError))
        .pipe(concat("app.css"))
        .pipe(postcss(postcssProcessors).on("error", logError))
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest("fanboi2/static"));
}

function styleAdmin() {
    return gulp
        .src([
            "assets/admin/stylesheets/*.scss",
            "assets/admin/stylesheets/themes/*.scss"
        ])
        .pipe(sourcemaps.init())
        .pipe(sass().on("error", sass.logError))
        .pipe(concat("admin.css"))
        .pipe(postcss(postcssProcessors).on("error", logError))
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest("fanboi2/static"));
}

function styleVendor() {
    return gulp
        .src("assets/vendor/**/*.css")
        .pipe(sourcemaps.init())
        .pipe(concat("vendor.css"))
        .pipe(postcss(postcssProcessors).on("error", logError))
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest("fanboi2/static"));
}

var styles = gulp.series(assets, gulp.parallel(styleApp, styleAdmin, styleVendor));

/* Scripts
 * -------------------------------------------------------------------------------- */

var externalDependencies = [
    "dom4",
    "domready",
    "es6-promise",
    "js-cookie",
    "virtual-dom"
];

var scriptApp = function() {
    return browserify({ debug: true })
        .plugin(tsify)
        .require("assets/app/javascripts/app.ts", { entry: true })
        .external(externalDependencies)
        .bundle()
        .on("error", logError)
        .pipe(source("app.js"))
        .pipe(buffer())
        .pipe(sourcemaps.init({ loadMaps: true }))
        .pipe(uglify())
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest("fanboi2/static"));
};

var scriptLegacy = function() {
    return gulp
        .src("assets/legacy/**/*.js")
        .pipe(sourcemaps.init())
        .pipe(concat("legacy.js"))
        .pipe(uglify())
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest("fanboi2/static"));
};

var scriptVendor = function() {
    return browserify({ debug: true })
        .require(externalDependencies)
        .bundle()
        .on("error", logError)
        .pipe(source("vendor.js"))
        .pipe(buffer())
        .pipe(sourcemaps.init({ loadMaps: true }))
        .pipe(uglify())
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest("fanboi2/static"));
};

var scripts = gulp.parallel(scriptApp, scriptLegacy, scriptVendor);

/* Build
 * -------------------------------------------------------------------------------- */

var build = gulp.parallel(styles, scripts);

function watch() {
    gulp.watch("assets/app/**/*.scss", styles);
    gulp.watch("assets/admin/**/*.scss", styles);
    gulp.watch("assets/vendor/**/*.css", styles);

    gulp.watch("assets/app/**/*.ts", scripts);
    gulp.watch("assets/vendor/**/*.js", scripts);
    gulp.watch("assets/legacy/**/*.js", scripts);
}

/* Exports
 * -------------------------------------------------------------------------------- */

exports.watch = watch;
exports.build = build;
exports.assets = assets;
exports.styles = styles;
exports.scripts = scripts;

/* Default task */
exports.default = build;
