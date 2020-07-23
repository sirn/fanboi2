<%namespace name='datetime' file='../partials/_datetime.mako' />
<%namespace name='post' file='../partials/_post.mako' />
<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>${board.title}</%def>
% for topic in topics:
    <div data-topic="${topic.id}">
        <div class="panel util-padded">
            <div class="container">
                <h3 class="panel__item util-text-normal"><a href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">${topic.title}</a></h3>
                <p class="panel__item">${topic.meta.post_count} posts at ${datetime.render_datetime(topic.meta.posted_at)}</p>
            </div>
        </div>
        % for p in topic.recent_posts(5):
            ${post.render_post(topic, p, shorten=500)}
        % endfor
        <div class="panel panel--tint util-padded">
            <div class="container">
                <a class="button button--action button--mobile-block" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">Recent posts</a>
                <a class="button button--action button--mobile-block" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">All posts</a>
                <a class="button button--success button--mobile-block" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}#reply">Reply</a>
            </div>
        </div>
    </div>
% endfor
