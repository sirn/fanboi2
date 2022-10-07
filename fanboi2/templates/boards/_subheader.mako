<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="subheader" file="../partials/_subheader.mako" />
<%subheader:render_subheader title="${board.title}" href="${request.route_path('board', board=board.slug)}">
    <%def name="description()">
        ${formatters.format_markdown(request, board.description)}
    </%def>
    <%def name="buttons()">
        ${subheader.render_button("Recent topics", request.route_path('board', board=board.slug), route_name="board")}
        ${subheader.render_button("All topics", request.route_path('board_all', board=board.slug), route_name="board_all")}
        % if board.status == 'open':
            ${subheader.render_button("New topic", request.route_path('board_new', board=board.slug), route_name="board_new")}
        % endif
    </%def>
</section>
</%subheader:render_subheader>
