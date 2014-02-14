$(document).ready(function(){

    $header = document.getElementById('header');
    if ($header) {
        var HeaderView = require('views/header_view');
        new HeaderView({el: $header}).render();
    }

    $topics = document.getElementsByClassName('container-topic');
    if ($topics.length) {
        var TopicView = require('views/topic_view');
        _.map($topics, function($el) { new TopicView({el: $el}); });
    }

});
