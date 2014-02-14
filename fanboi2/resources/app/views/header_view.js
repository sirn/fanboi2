module.exports = Backbone.View.extend({

    events: {},

    render: function() {
        this._renderNavigator();
        this._renderBoardsMenu();
    },

    _renderNavigator: function() {
        console.log(this.$el);
    },

    _renderBoardsMenu: function() {
        console.log(this);
    }

});
