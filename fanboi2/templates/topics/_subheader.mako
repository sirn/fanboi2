<%namespace name="datetime" file="../partials/_datetime.mako" />
<header class="panel panel--inverse panel--bordered">
    <div class="container">
        <h3 class="panel__item"><a class="util-text-gray" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">${topic.title}</a></h3>
        <p class="panel__item util-text-gray">${topic.meta.post_count} posts at ${datetime.render_datetime(topic.meta.posted_at)}</p>
        <ul class="tabs">
            <li class="tabs__item"><a href="${request.route_path('board', board=board.slug)}">Back to board</a></li>
            <li class="tabs__item tabs__item--current"><a href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">Recent posts</a></li>
            <li class="tabs__item"><a href="#reply">Reply</a></li>
        </ul>
    </div>
</header>
