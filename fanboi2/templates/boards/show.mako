<%namespace name="formatters" module="fanboi2.formatters" />
<%namespace name="posts" file="../partials/_posts.mako" />
<%inherit file="../partials/_layout.mako" />
<%include file="_header.mako" />
<%def name="title()">${board.title}</%def>
% for topic in topics:
    <div id="topic-${topic.id}">
        <header class="header-posts">
            <div class="container">
                <a class="title" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">${topic.title}</a>
                <ul class="details">
                    <li>Last posted ${formatters.format_datetime(request, topic.posted_at)}</li>
                    <li>Total of <strong>${topic.post_count} posts</strong></li>
                </ul>
            </div>
        </header>
        ${posts.render_posts(topic, topic.recent_posts(5), shorten=500)}
        <footer class="footer-posts">
            <div class="container">
                <a class="button" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">Recent posts</a>
                <a class="button" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">All posts</a>
                <a class="button button-reply" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}#reply">Reply</a>
            </div>
        </footer>
    </div>
% endfor
