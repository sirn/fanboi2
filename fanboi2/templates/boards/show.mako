<%namespace name="datetime" file="../partials/_datetime.mako" />
<%namespace name="post" file="../partials/_post.mako" />
<%include file="_subheader.mako" />
<%inherit file="../partials/_layout.mako" />
<%def name="title()">${board.title}</%def>
% for topic in topics:
    <div data-topic="${topic.id}">
        <div class="panel panel--shade1">
            <div class="container u-pd-vertical-m">
                <h3 class="panel__item"><a href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">${topic.title}</a></h3>
                <div class="panel__item u-txt-s u-txt-gray4">
                    <ul class="list">
                        <li class="list__item">Last posted <strong>${datetime.render_datetime(topic.meta.posted_at)}</strong></li>
                        <li class="list__item">Total of <strong>${topic.meta.post_count} posts</strong></li>
                    </ul>
                </div>
            </div>
        </div>
        % for p in topic.recent_posts(5):
            ${post.render_post(topic, p, shorten=500)}
        % endfor
        <div class="panel panel--shade3">
            <div class="container u-pd-vertical-l">
                <div class="panel__item">
                    <ul class="list flex flex--column-mobile flex--row-tablet flex--gap-xs">
                        <li class="list__item flex__item"><a class="btn btn--shadowed btn--block-mobile" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">Recent posts</a></li>
                        <li class="list__item flex__item"><a class="btn btn--shadowed btn--block-mobile" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">All posts</a></li>
                        <li class="list__item flex__item"><a class="btn btn--shadowed btn--block-mobile btn--primary" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}#reply">Reply</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
% endfor
