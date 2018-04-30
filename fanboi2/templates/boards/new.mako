<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>New topic - ${board.title}</%def>
<div class="board-agreement sheet alternate">
    <div class="container">
        <h2 class="sheet-title">New topic</h2>
        <div class="sheet-body">${formatters.format_markdown(request, board.agreements)}</div>
        <div class="board-agreement-notice sheet-body">
            <p>You are agree to above agreement by posting. If you do not, you may go back now.</p>
            <a class="button muted" href="${request.route_path('board', board=board.slug)}">I disagree</a>
        </div>
    </div>
</div>
<form class="form" action="${request.route_path('board_new', board=board.slug)}" method="post">
    <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
    <div class="container">
        <div class="form-item${' error' if form.title.errors else ''}">
            <label class="form-item-label" for="${form.title.id}">Topic</label>
            ${form.title(class_="input block larger")}
            % if form.title.errors:
                <span class="form-item-error">${form.title.errors[0]}</span>
            % endif
        </div>
        <div class="form-item${' error' if form.body.errors else ''}">
            <label class="form-item-label" for="${form.body.id}">Body</label>
            ${form.body(class_="input block content", rows=6)}
            % if form.body.errors:
                <span class="form-item-error">${form.body.errors[0]}</span>
            % endif
        </div>
        <div class="form-item">
            <button class="button brand" type="submit">New Topic</button>
        </div>
    </div>
</form>
