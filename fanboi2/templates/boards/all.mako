<%namespace name="formatters" module="fanboi2.formatters" />
<%inherit file="../partials/_layout.mako" />
<%include file="_header.mako" />
% for topic in topics:
    <div class="item-topic" id="topic-${topic.id}">
        <div class="container">
            <a class="title" href="${request.route_path('topic_scoped', board=board.slug, topic=topic.id, query='recent')}">${topic.title}</a>
            <ul class="details">
                <li>Last posted ${formatters.format_datetime(request, topic.posted_at)}</li>
                <li>Total of <strong>${topic.post_count} posts</strong></li>
            </ul>
        </div>
    </div>
% endfor
