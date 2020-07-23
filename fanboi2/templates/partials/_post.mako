<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="datetime" file="_datetime.mako" />
<%namespace name="ident" file="_ident.mako" />
<%def name="render_post(topic, post, shorten=None)">
    <div class="panel panel--bordered panel--inverse">
        <div class="container">
            <div class="post">
                <div class="panel__item">
                    <a class="post__item ${'post__item--bumped' if post.bumped else 'post__item--saged'}" href="${request.route_path('topic_scoped', board=post.topic.board.slug, topic=post.topic.id, query=post.number)}" data-topic-quick-reply="${post.number}">${post.number}</a>
                    <span class="post__item post__item--name">${post.name}</span>
                    <span class="post__item post__item--datetime">Posted ${datetime.render_datetime(post.created_at)}</span>
                    ${ident.render_ident(post.ident, post.ident_type, class_='post__item')}
                </div>
                <div class="panel__item post__container">
                    ${formatters.format_post(request, post, shorten=shorten)}
                </div>
            </div>
        </div>
    </div>
</%def>
