var gulp = require("gulp");
var sourcemaps = require("gulp-sourcemaps");
var concat = require("gulp-concat");
var postcss = require("gulp-postcss");
var uglify = require("gulp-uglify");
var source = require("vinyl-source-stream");
var buffer = require("vinyl-buffer");
var browserify = require("browserify");
var tsify = require("tsify");
var del = require("del");

/* Utils
 * -------------------------------------------------------------------------------- */

function logError(error) {
    console.log(error);
    this.emit("end");
}

/* Assets
 * -------------------------------------------------------------------------------- */

function assets() {
    return gulp.src("assets/assets/*").pipe(gulp.dest("fanboi2/static"));
}

/* Styles
 * -------------------------------------------------------------------------------- */

var pc = require("postcss");
var spriteUpdateRule = require("postcss-sprites/lib/core").updateRule;

var postcssProcessors = [
    require("postcss-import"),
    require("postcss-mixins"),
    require("postcss-nested"),
    require("lost"),
    /* Note: allowDuplicates is needed to allow reload to work properly. */
    require("postcss-normalize")({ allowDuplicates: true }),
    require("postcss-utilities")({ textHideMethod: "font" }),
    require("postcss-custom-media"),
    require("postcss-custom-properties")({ preserve: false }),
    require("postcss-color-function"),
    require("postcss-calc"),
    require("postcss-image-set-polyfill"),
    require("postcss-url")({
        url: function (asset, dir, options, decl, warn, result) {
            /* PostCSS-Sprites require absolute path to work with baseDir. */
            if (asset.url.match("^[^/]")) {
                return "/" + asset.url;
            }
        },
    }),
    require("postcss-sprites")({
        stylesheetPath: "fanboi2/static",
        spritePath: "fanboi2/static",
        basePath: "assets/assets",
        retina: true,
        spritesmith: { padding: 5 },
        hooks: {
            onUpdateRule: function (rule, token, image) {
                spriteUpdateRule(rule, token, image);
                rule.insertAfter(
                    rule.last,
                    pc.decl({
                        prop: "background-repeat",
                        value: "no-repeat",
                    })
                );
                ["width", "height"].forEach(function (prop) {
                    var value = image.coords[prop];
                    if (image.retina) {
                        value /= image.ratio;
                    }
                    rule.insertAfter(
                        rule.last,
                        pc.decl({
                            prop: prop,
                            value: value + "px",
                        })
                    );
                });
            },
        },
    }),
    require("postcss-round-subpixels"),
    require("mqpacker"),
    require("postcss-urlrev")({
        relativePath: "fanboi2/static",
        replacer: function (url, hash) {
            /* PostCSS-Urlrev uses ?v= by default. Override to
             * make it compatible with ?h= syntax in app. */
            return url + "?h=" + hash.slice(0, 8);
        },
    }),
    require("autoprefixer"),
    require("colorguard")({
        allowEquivalentNotation: true,
        ignore: ["#dfe7ec", "#eff3f5"],
    }),
    require("postcss-discard-unused"),
    require("postcss-merge-idents"),
    require("postcss-reduce-idents"),
    require("postcss-zindex"),
    require("cssnano")({
        preset: [
            "default",
            {
                discardComments: {
                    removeAll: true,
                },
            },
        ],
    }),
];

function styleApp() {
    return gulp
        .src("assets/stylesheets/app.css")
        .pipe(sourcemaps.init())
        .pipe(postcss(postcssProcessors).on("error", logError))
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest("fanboi2/static"));
}

// This is needed in case we're running on NFS mount otherwise files
// won't get triggered for an update.
var styleClean = function () {
    return del(["fanboi2/static/app.css", "fanboi2/static/app.css.map"]);
};

var styles = gulp.series(styleClean, assets, gulp.parallel(styleApp));

/* Scripts
 * -------------------------------------------------------------------------------- */

var externalDependencies = [
    "dom4",
    "domready",
    "es6-promise",
    "js-cookie",
    "virtual-dom",
];

var scriptApp = function () {
    return browserify({ debug: true })
        .plugin(tsify)
        .require("assets/javascripts/app.ts", { entry: true })
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

// This is needed in case we're running on NFS mount otherwise files
// won't get triggered for an update.
var scriptClean = function () {
    return del(["fanboi2/static/app.js", "fanboi2/static/app.js.map"]);
};

var scripts = gulp.series(scriptClean, scriptApp);

/* Build
 * -------------------------------------------------------------------------------- */

var build = gulp.parallel(styles, scripts);

var clean = gulp.series(styleClean, scriptClean);

function watch() {
    gulp.watch("assets/stylesheets/**/*.css", styles);
    gulp.watch("assets/javascripts/**/*.ts", scripts);
}

/* Exports
 * -------------------------------------------------------------------------------- */

exports.watch = watch;
exports.build = build;
exports.assets = assets;
exports.styles = styles;
exports.scripts = scripts;
exports.clean = clean;

/* Default task */
exports.default = build;
