<div class="sheet-body">
    <a class="button" href="${request.route_path('admin_boards')}">All Boards</a>
    <a class="button green" href="${request.route_path('admin_board_new')}">New Board</a>
    % if board:
    <div class="admin-button-context">
        <a class="button muted admin-button-context" href="${request.route_path('admin_board_topics', board=board.slug)}">All Topics</a>
    </div>
    % endif
</div>