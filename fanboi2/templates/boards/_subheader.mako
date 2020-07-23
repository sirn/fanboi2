<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<header class="panel panel--inverse">
    <div class="container">
        <h2 class="panel__item"><a class="util-text-gray" href="${request.route_path('board', board=board.slug)}">${board.title}</a></h2>
        <p class="panel__item util-text-gray">${board.description}</p>
        <div class="panel__item">
            <ul class="tabs">
                <li class="tabs__item${' tabs__item--current' if request.route_name == 'board' else ''}"><a href="${request.route_path('board', board=board.slug)}">Recent topics</a></li>
                <li class="tabs__item${' tabs__item--current' if request.route_name == 'board_all' else ''}"><a href="${request.route_path('board_all', board=board.slug)}">All topics</a></li>
                % if board.status == 'open':
                    <li class="tabs__item${' tabs__item--current' if request.route_name == 'board_new' else ''}"><a href="${request.route_path('board_new', board=board.slug)}">New topic</a></li>
                % endif
            </ul>
        </div>
    </div>
</header>
