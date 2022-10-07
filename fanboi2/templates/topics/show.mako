<%namespace name="post" file="../partials/_post.mako" />
<%namespace name="formtpl" file="../partials/_form.mako" />
<%include file="_subheader.mako" />
<%inherit file="../partials/_layout.mako" />
<%def name="title()">${topic.title} - ${board.title}</%def>
<%def name="body_args()" filter="n">data-topic="${topic.id}"</%def>
<%def name="header()"><link rel="canonical" href="${request.route_url("topic", board=board.slug, topic=topic.id)}"></%def>
% if posts:
    % if posts[0].number != 1:
    <div class="panel panel--separator panel--unit-link panel--shade3">
        <div class="container">
            <div class="post">
                <a class="panel__link" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query="1-%s" % posts[-1].number)}">
                    % if posts[0].number <= 2:
                        <span class="post__item post__item--bumped u-mg-right-xs">1</span>
                        <span class="post__item u-txt-gray4">Load previous post</span>
                    % else:
                        <span class="post__item post__item--bumped u-mg-right-xs">1-${posts[0].number - 1}</span>
                        <span class="post__item u-txt-gray4">Load previous posts</span>
                    % endif
                </a>
            </div>
        </div>
    </div>
    % endif
    % for p in posts:
        ${post.render_post(topic, p)}
    % endfor
    <div class="panel panel--shade3">
        <div class="container u-pd-vertical-l">
            <ul class="list flex flex--column-mobile flex--row-tablet flex--gap-xs">
                <li class="list__item flex__item"><a class="btn btn--shadowed btn--block-mobile" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">Recent posts</a></li>
                <li class="list__item flex__item"><a class="btn btn--shadowed btn--block-mobile" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">All posts</a></li>
                % if posts and topic.status == 'open' and posts[-1].number == topic.meta.post_count:
                    <li class="list__item flex__item"><a class="btn btn--shadowed btn--block-mobile btn--brand" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query="%s-" % topic.meta.post_count)}" data-topic-reloader="true">Reload posts</a></li>
                % elif posts and posts[-1].number != topic.meta.post_count:
                    <li class="list__item flex__item"><a class="btn btn--shadowed btn--block-mobile" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query="%s-" % posts[-1].number)}" data-topic-reloader="true" data-topic-reloader-label="Reload posts" data-topic-reloader-class="btn btn--shadowed btn--block-mobile btn--brand">Newer posts</a></li>
                % endif
            </ul>
        </div>
    </div>
% endif
% if topic.status == 'locked':
    <div class="panel">
        <div class="container flex flex--column flex--gap-xs u-pd-vertical-l">
            <h2 class="panel__item flex__item u-txt-brand">Topic locked</h2>
            <p class="panel__item flex__item">Topic has been locked by moderator.</p>
            <p class="panel__item flex__item"><em>No more posts could be made at this time.</em></p>
        </div>
    </div>
% elif topic.status == 'archived':
    <div class="panel">
        <div class="container flex flex--column flex--gap-xs u-pd-vertical-l">
            <h2 class="panel__item flex__item u-txt-brand">Posts limit exceeded</h2>
            <p class="panel__item flex__item">Topic has reached maximum number of posts.</p>
            % if board.status == 'restricted':
                <p class="panel__item flex__item"><em>Please request to start a new topic with moderator.</em></p>
            % else:
                <p class="panel__item flex__item"><em>Please start a new topic.</em></p>
            % endif
        </div>
    </div>
% elif topic.status == 'expired':
    <div class="panel">
        <div class="container flex flex--column flex--gap-xs u-pd-vertical-l">
            <h2 class="panel__item flex__item u-txt-brand">Topic expired</h2>
            <p class="panel__item flex__item">Topic has reached inactivity threshold.</p>
            <p class="panel__item flex__item"><em>Please start a new topic.</em></p>
        </div>
    </div>
% elif board.status == 'locked':
    <div class="panel">
        <div class="container flex flex--column flex--gap-xs u-pd-vertical-l">
            <h2 class="panel__item flex__item u-txt-brand">Board locked</h2>
            <p class="panel__item flex__item">Board has been locked by moderator.</p>
            <p class="panel__item flex__item"><em>No more posts could be made at this time.</em></p>
        </div>
    </div>
% elif board.status == 'archived':
    <div class="panel">
        <div class="container flex flex--column flex--gap-xs u-pd-vertical-l">
            <h2 class="panel__item flex__item u-txt-brand">Board archived</h2>
            <p class="panel__item flex__item">Board has been archived</p>
            <p class="panel__item flex__item"><em>Topic is read-only.</em></p>
        </div>
    </div>
% else:
    <div class="panel">
        <div class="container u-pd-vertical-l">
            <div class="panel__item">
                <%formtpl:render_form href="${request.route_path('topic', board=board.slug, topic=topic.id)}">
                    <%formtpl:render_field form="${form}" label="Reply" field_extra_classes="form__input--bordered" field="body" rows="4" />
                    <%formtpl:render_button form="${form}" label="Post Reply" color="primary">
                        <%def name="inline_fields()">
                            <%formtpl:render_inline_field form="${form}" field="bumped" data_topic_state_tracker="bumped" />
                        </%def>
                    </%formtpl:render_button>
                </%formtpl:render_form>
            </div>
        </div>
    </div>
% endif
