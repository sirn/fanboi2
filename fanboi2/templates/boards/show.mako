<%namespace name="formatters" module="fanboi2.formatters" />
<%inherit file="../partials/_layout.mako" />
<%include file="_header.mako" />

% for topic in topics:
    <div id="topic-${topic.id}">
        <header class="header-topic">
            <div class="container">
                <a class="title" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">${topic.title}</a>
                <p class="description">Last posted ${formatters.format_datetime(request, topic.posted_at)}, total of <strong>${topic.post_count} posts</strong>.</p>
            </div>
        </header>
        % for post in topic.recent_posts(5):
            <div id="post-${post.id}" class="item-post">
                <div class="container">
                    <div class="item-post-meta">
                        <a class="item-post-number${' item-post-bumped' if post.bumped else ''}" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query=post.number)}">${post.number}</a>
                        <span class="item-post-name">${post.name}</span>
                        <time class="item-post-date" datetime="${formatters.format_isotime(request, post.created_at)}">Posted ${formatters.format_datetime(request, post.created_at)}</time>
                        <span class="item-post-ident">ID:${post.ident}</span>
                    </div>
                    <div class="item-post-body">${formatters.format_post(request, post, shorten=500)}</div>
                </div>
            </div>
        % endfor
        <footer class="footer-topic">
            <div class="container">
                <a class="button" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">Recent posts</a>
                <a class="button" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">All posts</a>
                <a class="button button-reply" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}#reply">Reply</a>
            </div>
        </footer>
    </div>
% endfor
