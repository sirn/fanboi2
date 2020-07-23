<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>New topic - ${board.title}</%def>
<form class="panel" action="${request.route_path('board_new', board=board.slug)}" method="post">
    <div class="container">
        <h2 class="panel__item util-padded util-text-gray">New topic</h2>
        % if board.agreements:
            <div class="panel__item util-padded-bottom">
                ${formatters.format_markdown(request, board.agreements)}
            </div>
        % endif
        <div class="panel__item util-padded-bottom">
            <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
            <div class="form-group${' form-group--error' if form.title.errors else ''}">
                <label class="form-group__label" for="${form.title.id}">Topic</label>
                ${form.title(class_="form-group__input")}
                % if form.title.errors:
                    <span class="form-group__hint">${form.title.errors[0]}</span>
                % endif
            </div>
            <div class="form-group${' error' if form.body.errors else ''}">
                <label class="form-group__label" for="${form.body.id}">Body</label>
                ${form.body(class_="form-group__input", rows=8)}
                % if form.body.errors:
                    <span class="form-group__hint">${form.body.errors[0]}</span>
                % endif
            </div>
            <div class="form-group">
                <button class="button button--primary" type="submit">New Topic</button>
            </div>
        </div>
    </div>
</form>
