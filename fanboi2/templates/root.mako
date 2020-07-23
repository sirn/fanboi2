<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%inherit file='partials/_layout.mako' />
<header class="panel panel--inverse">
    <div class="container">
        <h2 class="panel__item panel__item--header util-text-gray">Welcome, stranger!</h2>
        <p class="panel__item panel__item--subheader util-padded-bottom util-text-gray">Choose some board to begin.</p>
    </div>
</header>
<div class="container">
    % for board in boards:
        <div class="panel panel--bordered panel--unit-link">
            <h3 class="panel__item util-padded-top"><a class="panel__link" href="${request.route_path('board', board=board.slug)}">${board.title}</a></h3>
            <p class="panel__item util-padded-bottom">${board.description}</p>
        </div>
    % endfor
</div>
