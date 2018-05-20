<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="datetime" file="_datetime.mako" />
<%namespace name="ident" file="_ident.mako" />
<%def name="render_post(topic, post, shorten=None)">
    <div class="post">
        <div class="container">
            <div class="post-header">
                <a href="${request.route_path('topic_scoped', board=post.topic.board.slug, topic=post.topic.id, query=post.number)}" class="post-header-item number${' bumped' if post.bumped else ''}" data-topic-quick-reply="${post.number}">${post.number}</a>
                <span class="post-header-item name">${post.name}</span>
                <span class="post-header-item date">Posted ${datetime.render_datetime(post.created_at)}</span>
                ${ident.render_ident(post.ident, post.ident_type, class_='post-header-item')}
            </div>
            <div class="post-body">
                ${formatters.format_post(request, post, shorten=shorten)}
            </div>
        </div>
    </div>
</%def>
