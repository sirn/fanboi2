<%namespace name="formatters" module="fanboi2.formatters" />
<%def name="render_posts(topic, posts, shorten=None)">
    % for post in posts:
        <div id="post-${post.id}" class="item-post">
            <div class="container">
                <div class="item-post-meta">
                    <a class="item-post-number${' item-post-bumped' if post.bumped else ''}" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query=post.number)}">${post.number}</a>
                    <span class="item-post-name">${post.name}</span>
                    <time class="item-post-date" datetime="${formatters.format_isotime(request, post.created_at)}">Posted ${formatters.format_datetime(request, post.created_at)}</time>
                    <span class="item-post-ident">ID:${post.ident}</span>
                </div>
                <div class="item-post-body">${formatters.format_post(request, post, shorten=shorten)}</div>
            </div>
        </div>
    % endfor
</%def>