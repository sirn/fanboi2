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
        before: []

    stylesheets:
      joinTo:
        'stylesheets/app.css': /\/(app|vendor)/
      order:
        before: [
          'app/stylesheets/elements.styl',
          'app/stylesheets/layout.styl']
        after: []

  modules:
    nameCleaner: (path) ->
      path.replace(/^fanboi2\/resources\/(app|vendor)\//, '')
