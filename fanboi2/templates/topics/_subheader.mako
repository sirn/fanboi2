<%namespace name="formatters" module="fanboi2.formatters" />
<header class="subheader">
    <div class="container">
        <h2 class="subheader-title"><a href="${request.route_path('topic', board=board.slug, topic=topic.id)}">${topic.title}</a></h2>
        <div class="subheader-body">
            <p class="subheader-body-item">Last posted <strong>${formatters.format_datetime(request, topic.posted_at)}</strong></p>
            <p class="subheader-body-item">Total of <strong>${topic.post_count} posts</strong></p>
        </div>
        <div class="subheader-footer">
            <ul class="actions">
                <li class="actions-item"><a class="button" href="${request.route_path('board', board=board.slug)}">Back</a></li>
                <li class="actions-item"><a class="button primary" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">Show topic</a></li>
                <li class="actions-item"><a class="button reply" href="#reply">Reply</a></li>
            </ul>
        </div>
    </div>
</header>
