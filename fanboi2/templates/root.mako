<%namespace name="formatters" module="fanboi2.formatters" />
<%inherit file="partials/_layout.mako" />
<header class="header header-boards">
    <div class="container">
        <p>Please select category from list below.</p>
    </div>
</header>
% for board in boards:
    <div class="item-board" id="board-${board.slug}">
        <div class="container">
            <a class="title" href="${request.route_path('board', board=board.slug)}">${board.title}</a>
            <div class="description">${formatters.format_markdown(request, board.description)}</div>
        </div>
    </div>
% endfor
