<%namespace name="post" file="../partials/_post.mako" />
<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>${topic.title} - ${board.title}</%def>
% if posts:
    ${post.render_posts(topic, posts)}
% endif
<div class="topic-footer">
    <div class="container">
        <ul class="actions">
            <li class="actions-item"><a class="button" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">Latest posts</a></li>
            <li class="actions-item"><a class="button" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">All posts</a></li>
            % if posts and topic.status == 'open' and posts[-1].number == topic.post_count:
                <li class="actions-item"><a class="button primary" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query="%s-" % topic.post_count)}">Reload posts</a></li>
            % elif posts and posts[-1].number != topic.post_count:
                <li class="actions-item"><a class="button" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query="%s-" % posts[-1].number)}">Newer posts</a></li>
            % endif
        </ul>
    </div>
</div>
% if topic.status == 'open':
    <form class="form" id="reply" action="${request.route_path('topic', board=board.slug, topic=topic.id)}" method="post">
        <div class="container">
            <div class="form-item">
                <label class="form-item-label" for="${form.body.id}">Reply</label>
                ${form.body(class_='input block content', rows=4)}
                % if form.body.errors:
                    <span class="form-field-error">${form.body.errors[0]}</span>
                % endif
            </div>
            <div class="form-item">
                <button class="button" type="submit">Post Reply</button>
                ${form.bumped} <label for="${form.bumped.id}">${form.bumped.label.text}</label>
            </div>
        </div>
    </form>
% elif topic.status == 'locked':
    <div class="sheet">
        <div class="container">
            <h2 class="sheet-title">Topic locked</h2>
            <div class="sheet-body"><p>Topic has been locked by moderator. More posts could not be made at this time.</p></div>
        </div>
    </div>
% elif topic.status == 'archived':
    <div class="sheet">
        <div class="container">
            <h2 class="sheet-title">Posts limit exceeded</h2>
            <div class="sheet-body"><p>Topic has reached maximum number of posts. Please start a new topic.</p></div>
        </div>
    </div>
% endif
