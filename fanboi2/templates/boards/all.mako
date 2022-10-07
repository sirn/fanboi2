<%namespace name="datetime" file="../partials/_datetime.mako" />
<%inherit file="../partials/_layout.mako" />
<%include file="_subheader.mako" />
<%def name="title()">All topics - ${board.title}</%def>
% for topic in topics:
    <div class="panel panel--separator panel--unit-link">
        <div class="container u-pd-vertical-m">
            <h3 class="panel__item"><a class="panel__link" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">${topic.title}</a></h3>
            <div class="panel__item u-txt-s u-txt-gray4">
                <ul class="list">
                    <li class="list__item">Last posted <strong>${datetime.render_datetime(topic.meta.posted_at)}</strong></li>
                    <li class="list__item">Total of <strong>${topic.meta.post_count} posts</strong></li>
                </ul>
            </div>
        </div>
    </div>
% endfor
