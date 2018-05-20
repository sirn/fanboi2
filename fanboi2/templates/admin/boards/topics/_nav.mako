<div class="sheet-body">
    <a class="button" href="${request.route_path('admin_board_topics', board=board.slug)}">All Topics</a>
    <a class="button green" href="${request.route_path('admin_board_topic_new', board=board.slug)}">New Topic</a>
    <div class="admin-button-context">
        <a class="button muted" href="${request.route_path('admin_board', board=board.slug)}">Board</a>
    </div>
</div>