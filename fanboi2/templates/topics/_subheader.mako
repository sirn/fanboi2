<%namespace name="subheader" file="../partials/_subheader.mako" />
<%namespace name="datetime" file="../partials/_datetime.mako" />
<%subheader:render_subheader title="${topic.title}" href="${request.route_path('topic', board=board.slug, topic=topic.id)}">
    <%def name="description()">
        <ul class="list">
            <li class="list__item">Last posted <strong>${datetime.render_datetime(topic.meta.posted_at)}</strong></li>
            <li class="list__item">Total of <strong>${topic.meta.post_count} posts</strong></li>
        </ul>
    </%def>
    <%def name="buttons()">
        ${subheader.render_button("Back", request.route_path('board', board=board.slug), extra_class="btn--dark")}
        ${subheader.render_button("Show topic", request.route_path('topic', board=board.slug, topic=topic.id), extra_class="btn--brand")}
        % if topic.status == 'open' and board.status in ('open', 'restricted'):
            ${subheader.render_button("Reply", '#reply', extra_class="btn--primary")}
        % endif
    </%def>
</%subheader:render_subheader>
