<%def name="render_nav(title=None, board=None)">
    <div class="panel u-mg-bottom-m">
        % if title:
            <h2 class="panel__item u-txt-brand u-mg-bottom-s">${title}</h2>
        % endif
        % if board:
            <div class="panel__item">
                <ul class="list flex flex--row flex--gap-xs">
                    <ul class="list__item flex__item"><a class="btn btn--bordered btn--shadowed" href="${request.route_path('admin_board_topics', board=board.slug)}">All Topics</a></ul>
                    <ul class="list__item flex__item"><a class="btn btn--shadowed btn--primary" href="${request.route_path('admin_board_topic_new', board=board.slug)}">New Topic</a></ul>
                    <ul class="list__item flex__item flex__item--grow-2"><a class="btn btn--shadowed btn--gray5 u-pull-right" href="${request.route_path('admin_board', board=board.slug)}">Board</a>
                </ul>
            </div>
        % endif
    </div>
</%def>
