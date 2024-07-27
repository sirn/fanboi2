const autoprefixer = require("autoprefixer");
const concat = require("gulp-concat");
const cssnano = require("cssnano");
const gulp = require("gulp");
const postcss = require("gulp-postcss");
const tailwindcss = require("tailwindcss");
const urlrev = require("postcss-urlrev");
const webpack = require("webpack-stream");
const webpackCompiler = require("webpack");

/* Utils
 * -------------------------------------------------------------------------------- */

const logError = (error) => {
    console.log(error);
    this.emit("end");
}

/* Assets
 * -------------------------------------------------------------------------------- */

const assets = () => {
    return gulp
        .src("assets/assets/**/*")
        .pipe(gulp.dest("fanboi2/static"));
}

/* Styles
 * -------------------------------------------------------------------------------- */

const styleMain = () => {
    return gulp
        .src(["assets/styles/main.css"])
        .pipe(postcss([
            tailwindcss,
            autoprefixer,
            urlrev({
                relativePath: "fanboi2/static",
                replacer: function (url, hash) {
                    /* PostCSS-Urlrev uses ?v= by default. Override to
                     * make it compatible with ?h= syntax in app. */
                    return url + "?h=" + hash.slice(0, 8);
                },
            }),
            cssnano,
        ], {}))
        .pipe(concat("app.css"))
        .pipe(gulp.dest("fanboi2/static"));
};

const styles = gulp.series(assets, styleMain);

/* Scripts
 * -------------------------------------------------------------------------------- */

const scriptMain = () => {
  return gulp
      .src("assets/scripts/main.ts", { entry: true, allowEmpty: true })
      .pipe(
          webpack(
              {
                  mode: "production",
                  module: {
                      rules: [{ test: /\.tsx?$/, use: "ts-loader", exclude: /node_modules/ }],
                  },
                  resolve: {
                      fallback: {
                          assert: require.resolve("assert"),
                          buffer: require.resolve("buffer"),
                          crypto: require.resolve("crypto-browserify"),
                          http: require.resolve("stream-http"),
                          https: require.resolve("https-browserify"),
                          os: require.resolve("os-browserify"),
                          stream: require.resolve("stream-browserify"),
                          url: require.resolve("url"),
                          zlib: require.resolve("browserify-zlib"),
                      },
                      extensions: [".tsx", ".ts", ".js"],
                  },
                  plugins: [
                      new webpackCompiler.ProvidePlugin({
                          process: "process/browser",
                          Buffer: ["buffer", "Buffer"],
                      }),
                  ],
                  performance: { hints: false },
                  optimization: {
                      runtimeChunk: "single",
                      splitChunks: {
                          chunks: "all",
                          maxInitialRequests: Infinity,
                          minSize: 2,
                          cacheGroups: {
                              vendor: {
                                  test: /[\\/]node_modules[\\/]/,
                                  name: "vendor",
                              },
                          },
                      },
                  },
                  output: {
                      filename: "[name].bundle.js",
                  },
              },
              webpackCompiler
          )
      )
      .pipe(gulp.dest("fanboi2/static"));
};

const scripts = gulp.parallel(scriptMain);

/* Build
 * -------------------------------------------------------------------------------- */

const build = gulp.parallel(styles, scripts);

function watch() {
    gulp.watch("assets/assets/**/*", assets);
    gulp.watch("assets/scripts/**/*.ts", scripts);
    gulp.watch("assets/styles/**/*.css", styles);

    /* This should match with modules.exports.content in tailwind.config.js */
    gulp.watch("assets/scripts/**/*.ts", styles);
    gulp.watch("fanboi2/templates/**/*.mako", styles);
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
