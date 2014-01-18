<%namespace name="formatters" module="fanboi2.formatters" />
<header class="header header-board">
    <div class="container">
        <a class="title" href="${request.route_path('board', board=board.slug)}">${board.title}</a>
        <div class="description">${formatters.format_markdown(request, board.description)}</div>
        <a class="button${' button-current' if request.route_name == 'board' else ''}" href="${request.route_path('board', board=board.slug)}">Recent topics</a>
        <a class="button${' button-current' if request.route_name == 'board_all' else ''}" href="${request.route_path('board_all', board=board.slug)}">All topics</a>
        <a class="button${' button-current' if request.route_name == 'board_new' else ''}" href="${request.route_path('board_new', board=board.slug)}">New topic</a>
    </div>
</header>
