module.exports = Backbone.View.extend({

    initialize: function() {
        $posts = this.$('.item-post');
        if ($posts.length) {
            var PostView = require('views/post_view');
            _.map($posts, function(el) { new PostView({el: el}); });
        }
    },

    events: {
        'click .button-reload': '_reloadTopic'
    },

    _reloadTopic: function(e) {
        e.preventDefault();
        console.log(e);
    }


});
