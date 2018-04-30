<%namespace name="post" file="../partials/_post.mako" />
<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>${topic.title} - ${board.title}</%def>
<%def name='body_args()'>data-topic="${topic.id}"</%def>
% if posts:
    ${post.render_posts(topic, posts)}
    <div class="topic-footer">
        <div class="container">
            <ul class="actions">
                <li class="actions-item"><a class="button action" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">Latest posts</a></li>
                <li class="actions-item"><a class="button action" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">All posts</a></li>
                % if posts and topic.status == 'open' and posts[-1].number == topic.meta.post_count:
                    <li class="actions-item"><a class="button brand" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query="%s-" % topic.meta.post_count)}" data-topic-reloader="true">Reload posts</a></li>
                % elif posts and posts[-1].number != topic.meta.post_count:
                    <li class="actions-item"><a class="button action" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query="%s-" % posts[-1].number)}" data-topic-reloader="true" data-topic-reloader-label="Reload posts" data-topic-reloader-class="button brand">Newer posts</a></li>
                % endif
            </ul>
        </div>
    </div>
% endif
% if topic.status == 'locked':
    <div class="sheet">
        <div class="container">
            <h2 class="sheet-title">Topic locked</h2>
            <div class="sheet-body">
                <p>Topic has been locked by moderator.</p>
                <p>No more posts could be made at this time.</p>
            </div>
        </div>
    </div>
% elif topic.status == 'archived':
    <div class="sheet">
        <div class="container">
            <h2 class="sheet-title">Posts limit exceeded</h2>
            <div class="sheet-body">
                <p>Topic has reached maximum number of posts.</p>
                % if board.status == 'restricted':
                    <p>Please request to start a new topic with moderator.</p>
                % else:
                    <p>Please start a new topic.</p>
                % endif
            </div>
        </div>
    </div>
% elif board.status == 'locked':
    <div class="sheet">
        <div class="container">
            <h2 class="sheet-title">Board locked</h2>
            <div class="sheet-body">
                <p>Board has been locked by moderator</p>
                <p>No more posts could be made at this time.</p>
            </div>
        </div>
    </div>
% elif board.status == 'archived':
    <div class="sheet">
        <div class="container">
            <h2 class="sheet-title">Board archived</h2>
            <div class="sheet-body">
                <p>Board has been archived</p>
                <p>Topic is read-only.</p>
            </div>
        </div>
    </div>
% else:
    <form class="form" id="reply" action="${request.route_path('topic', board=board.slug, topic=topic.id)}" method="post" data-topic-inline-reply="true">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="container">
            <div class="form-item${' error' if form.body.errors else ''}">
                <label class="form-item-label" for="${form.body.id}">Reply</label>
                ${form.body(class_='input block content', rows=4, **{'data-form-anchor': 'true', 'data-topic-quick-reply-input': 'true'})}
                % if form.body.errors:
                    <span class="form-item-error">${form.body.errors[0]}</span>
                % endif
            </div>
            <div class="form-item">
                <button class="button green" type="submit">Post Reply</button>
                <span class="form-item-inline">
                    ${form.bumped(**{'data-topic-state-tracker': "bump"})} <label for="${form.bumped.id}">${form.bumped.label.text}</label>
                </span>
            </div>
        </div>
    </form>
% endif