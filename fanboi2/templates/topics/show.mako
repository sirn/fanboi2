<%namespace name="formatters" module="fanboi2.formatters" />
<%namespace name="posts_" file="../partials/_posts.mako" />
<%inherit file="../partials/_layout.mako" />
<header class="header header-topic">
    <div class="container">
        <a class="title" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">${topic.title}</a>
        <p class="description">Last posted ${formatters.format_datetime(request, topic.posted_at)}, total of <strong>${topic.post_count} posts</strong>.</p>
        <a class="button" href="${request.route_path('board', board=board.slug)}">← ${board.title}</a>
        <a class="button button-current" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">All posts</a>
        <a class="button button-reply" href="#reply">Reply</a>
    </div>
</header>
${posts_.render_posts(topic, posts)}
<footer class="footer-posts">
    <div class="container">
        <a class="button" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">Recent posts</a>
        <a class="button" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">All posts</a>
        <a class="button button-reload" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query="%s-" % posts[-1].number)}">Reload post</a>
    </div>
</footer>
<div id="reply" class="reply-topic">
    <div class="container">
        <form action="${request.route_path('topic', board=board.slug, topic=topic.id)}" method="post" class="form">
            ${form.csrf_token}
            <div class="form-field">
                <label for="${form.body.id}">Reply</label>
                ${form.body}
                % if form.body.errors:
                    <span class="form-error">${form.errors[0]}</span>
                % endif
            </div>
            <div class="form-actions">
                <button type="submit" class="button button-reply">Post Reply</button>
                ${form.bumped} <label for="${form.bumped.id}" class="reply-topic-bump">${form.bumped.label.text}</label>
            </div>
        </form>
    </div>
</div>