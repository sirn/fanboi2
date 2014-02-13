<%namespace name="posts_" file="../partials/_posts.mako" />
<%inherit file="../partials/_layout.mako" />
<%include file="_header.mako" />
<%def name="title()">${topic.title} - ${board.title}</%def>
% if posts:
    ${posts_.render_posts(topic, posts)}
    <footer class="footer-posts">
        <div class="container">
            <a class="button" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">Recent posts</a>
            <a class="button" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">All posts</a>
            <a class="button button-reload" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query="%s-" % posts[-1].number)}">Reload post</a>
        </div>
    </footer>
% endif
<div id="reply" class="reply-topic">
    <div class="container">
        <form action="${request.route_path('topic', board=board.slug, topic=topic.id)}" method="post" class="form">
            ${form.csrf_token}
            <div class="form-field${' form-error' if form.body.errors else ''}">
                <label for="${form.body.id}">Reply</label>
                ${form.body}
                % if form.body.errors:
                    <span class="error-message">${form.body.errors[0]}</span>
                % endif
            </div>
            <div class="form-actions">
                <button type="submit" class="button button-post">Post Reply</button>
                ${form.bumped} <label for="${form.bumped.id}">${form.bumped.label.text}</label>
            </div>
        </form>
    </div>
</div>