<%namespace name="formatters" module="fanboi2.formatters" />
<header class="header header-topic">
    <div class="container">
        <a class="title" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">${topic.title}</a>
        <p class="description">Last posted ${formatters.format_datetime(request, topic.posted_at)}, total of <strong>${topic.post_count} posts</strong>.</p>
        <a class="button" href="${request.route_path('board', board=board.slug)}">← ${board.title}</a>
        <a class="button button-current" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">All posts</a>
        <a class="button button-reply" href="#reply">Reply</a>
    </div>
</header>
