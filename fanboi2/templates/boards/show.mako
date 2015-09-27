<%namespace name='formatters' module='fanboi2.formatters' />
<%namespace name='post' file='../partials/_post.mako' />
<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>${board.title}</%def>
% for topic in topics:
    <div class="topic">
        <div class="topic-header">
            <div class="container">
                <h3 class="topic-header-title"><a href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">${topic.title}</a></h3>
                <p class="topic-header-item">Last posted <strong>${formatters.format_datetime(request, topic.posted_at)}</strong></p>
                <p class="topic-header-item">Total of <strong>${topic.post_count} posts</strong></p>
            </div>
        </div>
        <div class="topic-body">
            ${post.render_posts(topic, topic.recent_posts(5), shorten=500)}
        </div>
        <div class="topic-footer">
            <div class="container">
                <ul class="actions">
                    <li class="actions-item"><a class="button action" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">Recent posts</a></li>
                    <li class="actions-item"><a class="button action" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">All posts</a></li>
                    <li class="actions-item"><a class="button green" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}#reply">Reply</a></li>
                </ul>
            </div>
        </div>
    </div>
% endfor
