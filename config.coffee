exports.config =
  paths:
    public: 'fanboi2/static'
    watched: ['fanboi2/resources']

  files:
    javascripts:
      joinTo:
        'javascripts/app.js': /\/app/
        'javascripts/vendor.js': /\/vendor/
      order:
        before: [
          'fanboi2/resources/vendor/javascripts/jquery.js',
          'fanboi2/resources/vendor/javascripts/lodash.js',
          'fanboi2/resources/vendor/javascripts/modernizr.js',
          'fanboi2/resources/vendor/javascripts/backbone.js']

    stylesheets:
      joinTo:
        'stylesheets/app.css': /\/(app|vendor)/
      order:
        before: []
        after: []

  modules:
    nameCleaner: (path) ->
      path.replace(/^fanboi2\/resources\/(app|vendor)\//, '')
