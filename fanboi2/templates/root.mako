<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%inherit file='partials/_layout.mako' />
<header class="subheader">
    <div class="container">
        <h2 class="subheader-title">Welcome, stranger!</h2>
        <div class="subheader-body">
            <p>Please choose the board from the list below.</p>
        </div>
    </div>
</header>
% for board in boards:
    <div class="cascade">
        <div class="container">
            <div class="cascade-header">
                <a class="cascade-header-link" href="${request.route_path('board', board=board.slug)}">${board.title}</a>
            </div>
            <div class="cascade-body">
                ${formatters.format_markdown(request, board.description)}
            </div>
        </div>
    </div>
% endfor
