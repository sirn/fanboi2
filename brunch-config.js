exports.config = {
    'paths': {
        'public': 'fanboi2/static',
        'watched': ['fanboi2/resources']
    },

    'plugins': {
        'postcss': {
            'processors': [
                require('autoprefixer'),
                require('postcss-round-subpixels'),
                require('css-mqpacker'),
                require('postcss-urlrev')({
                    replacer: function(url, hash) {
                        /* PostCSS-Urlrev uses ?v= by default. Override to
                         * make it compatible with ?h= syntax in app. */
                        return url + '?h=' + hash.slice(0, 8);
                    }
                }),
                require('csswring')
            ]
        }
    },

    'files': {
        'javascripts': {
            'joinTo': {
                'javascripts/app.js': /\/app/,
                'javascripts/legacy.js': /\/legacy/,
                'javascripts/vendor.js': /\/vendor/
            },
            'order': {
                'before': [],
                'after': []
            }
        },

        'stylesheets': {
            'joinTo': {
                'stylesheets/app.css': /\/(app|vendor)/,
                'stylesheets/legacy.css': /\/legacy/
            },
            'order': {
                'before': [
                    'fanboi2/resources/vendor/stylesheets/normalize.css',
                    'fanboi2/resources/app/stylesheets/app.scss'
                ],
                'after': [
                    /fanboi2\/resources\/app\/stylesheets\/themes\//
                ]
            }
        }
    },

    'modules': {
        'nameCleaner': function(path) {
            return path.replace(/^fanboi2\/resources\/(app|vendor)\//, '');
        }
    },

    /* Unfortunately useFsEvents doesn't work quite well on FreeBSD + NFS. */
    'watcher': {
        'usePolling': true
    }
};
