<%namespace name='datetime' file='../partials/_datetime.mako' />
<%inherit file='../partials/_layout.mako' />
<%include file='_subheader.mako' />
<%def name='title()'>All topics - ${board.title}</%def>
% for topic in topics:
    <div class="cascade">
        <div class="container">
            <div class="cascade-header">
                <a class="cascade-header-link" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">${topic.title}</a>
            </div>
            <div class="cascade-body">
                <p>Last posted ${datetime.render_datetime(topic.meta.posted_at)}</p>
                <p>Total of <strong>${topic.meta.post_count} posts</strong></p>
            </div>
        </div>
    </div>
% endfor
