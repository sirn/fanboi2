<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="datetime" file="_datetime.mako" />
<%namespace name="ident" file="_ident.mako" />
<%def name="render_post(topic, post, shorten=None)">
    <div class="panel panel--separator panel--shade2" data-post="${post.number}">
        <div class="container">
            <div class="post post--datetime-mobile">
                <div class="panel__item post__header">
                    <a class="post__item ${'post__item--bumped' if post.bumped else 'post__item--saged'} u-mg-right-xs" href="${request.route_path('topic_scoped', board=post.topic.board.slug, topic=post.topic.id, query=post.number)}" data-topic-reply="${post.number}">${post.number}</a>
                    <span class="post__item post__item--name u-mg-right-xs">${post.name}</span>
                    <span class="post__item post__item--datetime u-mg-right-xs-tablet">Posted ${datetime.render_datetime(post.created_at)}</span>
                    ${ident.render_ident(post.ident, post.ident_type, class_='post__item post__item--ident')}
                </div>
                <div class="panel__item post__container">
                    ${formatters.format_post(request, post, shorten=shorten)}
                </div>
            </div>
        </div>
    </div>
</%def>
