exports.config = {
    'paths': {
        'public': 'fanboi2/static',
        'watched': ['fanboi2/resources']
    },

    'plugins': {
        'postcss': {
            'processors': [
                require('autoprefixer'),
                require('csswring')
            ]
        }
    },

    'files': {
        'javascripts': {
            'joinTo': {
                'javascripts/app.js': /\/app/,
                'javascripts/vendor.js': /\/vendor/
            },
            'order': {
                'before': [],
                'after': []
            }
        },

        'stylesheets': {
            'joinTo': {
                'stylesheets/app.css': /\/(app|vendor)/
            },
            'order': {
                'before': [],
                'after': []
            }
        }
    },

    'modules': {
        'nameCleaner': function(path) {
            path.replace(/^fanboi2\/resources\/(app|vendor)\//, '');
        }
    }
};
