<%namespace name="formatters" module="fanboi2.formatters" />
<%def name="render_posts(topic, posts, shorten=None)">
    % for post in posts:
        <div class="post">
            <div class="container">
                <div class="post-header">
                    <a href="${request.route_path('topic_scoped', board=post.topic.board.slug, topic=post.topic.id, query=post.number)}" class="post-header-item number${' bumped' if post.bumped else ''}">${post.number}</a>
                    <span class="post-header-item name">${post.name}</span>
                    <time class="post-header-item date" datetime="${formatters.format_isotime(request, post.created_at)}">Posted ${formatters.format_datetime(request, post.created_at)}</time>
                    % if post.ident:
                        <span class="post-header-item ident">ID:${post.ident}</span>
                    % endif
                </div>
                <div class="post-body">
                    ${formatters.format_post(request, post, shorten=shorten)}
                </div>
            </div>
        </div>
    % endfor
</%def>
