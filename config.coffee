exports.config =
  paths:
    public: 'fanboi2/static'

  files:
    javascripts:
      joinTo:
        'javascripts/app.js': /^app/
        'javascripts/vendor.js': /^vendor/
      order:
        before: []

    stylesheets:
      joinTo:
        'stylesheets/app.css': /^(app|vendor)/
      order:
        before: [
          'vendor/stylesheets/reset.css',
          'app/stylesheets/elements.styl',
          'app/stylesheets/layout.styl']
        after: []
