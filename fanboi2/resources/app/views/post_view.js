module.exports = Backbone.View.extend({

    events: function() {
        var ev = {
            'click a.item-post-number':  '_openReplyBox',
            'click p.shortened a':       '_expandComment'
        };

        // Because touch events are annoying to deal with...
        if (Modernizr.touch) {
            return $.extend(ev, {
                'click a.anchor':        '_openCommentPopover',
                'click a.thumbnail':     '_openPreviewThumbnail'
            });
        } else {
            return $.extend(ev, {
                'mouseover a.anchor':    '_openCommentPopover',
                'mouseover a.thumbnail': '_openPreviewThumbnail'
            });
        }
    },

    _openCommentPopover: function(e) {
        e.preventDefault();
        console.log(e);
    },

    _openPreviewThumbnail: function(e) {
        e.preventDefault();
        console.log(e);
    },

    _openReplyBox: function(e) {
        e.preventDefault();
        console.log(e);
    },

    _expandComment: function(e) {
        e.preventDefault();
        console.log(e);
    }

});