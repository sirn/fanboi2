<%namespace name='datetime' file='../partials/_datetime.mako' />
<%namespace name='post' file='../partials/_post.mako' />
<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>${board.title}</%def>
% for topic in topics:
    <div class="topic" data-topic="${topic.id}">
        <div class="topic-header">
            <div class="container">
                <h3 class="topic-header-title"><a href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">${topic.title}</a></h3>
                <p class="topic-header-item">Last posted <strong>${datetime.render_datetime(topic.meta.posted_at)}</strong></p>
                <p class="topic-header-item">Total of <strong>${topic.meta.post_count} posts</strong></p>
            </div>
        </div>
        <div class="topic-body">
            % for p in topic.recent_posts(5):
                ${post.render_post(topic, p, shorten=500)}
            % endfor
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
