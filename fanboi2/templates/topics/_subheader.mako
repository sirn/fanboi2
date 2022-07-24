<%namespace name="datetime" file="../partials/_datetime.mako" />
<header class="subheader">
    <div class="container">
        <h2 class="subheader-title"><a href="${request.route_path('topic', board=board.slug, topic=topic.id)}">${topic.title}</a></h2>
        <div class="subheader-body lines">
            <p>Last posted <strong>${datetime.render_datetime(topic.meta.posted_at)}</strong></p>
            <p>Total of <strong>${topic.meta.post_count} posts</strong></p>
        </div>
        <div class="subheader-footer">
            <ul class="actions">
                <li class="actions-item"><a class="button default" href="${request.route_path('board', board=board.slug)}">Back</a></li>
                <li class="actions-item"><a class="button brand" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">Show topic</a></li>
                % if topic.status == 'open' and board.status in ('open', 'restricted'):
                    <li class="actions-item"><a class="button green static" href="#reply">Reply</a></li>
                % endif
            </ul>
        </div>
    </div>
</header>
