<%namespace name="formatters" module="fanboi2.formatters" />
<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>New topic - ${board.title}</%def>
<div class="sheet">
    <div class="container">
        <h2 class="sheet-title">New topic</h2>
        <div class="sheet-body">${formatters.format_markdown(request, board.agreements)}</div>
        <div class="sheet-body">
            <p>By continuing, you are agree to the above agreement. Otherwise, you may go back now.</p>
            <a class="button" href="${request.route_path('board', board=board.slug)}">Back</a>
        </div>
    </div>
</div>
<form class="form" action="${request.route_path('board_new', board=board.slug)}" method="post">
    <div class="container">
        <div class="form-item">
            <label class="form-item-label" for="${form.title.id}">Topic</label>
            ${form.title(class_='input block larger')}
            % if form.title.errors:
                <span class="form-field-error">${form.title.errors[0]}</span>
            % endif
        </div>
        <div class="form-item">
            <label class="form-item-label" for="${form.body.id}">Body</label>
            ${form.body(class_='input block content', rows=6)}
            % if form.body.errors:
                <span class="form-field-error">${form.body.errors[0]}</span>
            % endif
        </div>
        <div class="form-item">
            <button class="button" type="submit">New Topic</button>
        </div>
    </div>
</form>
