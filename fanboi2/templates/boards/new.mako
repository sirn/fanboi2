<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>New topic - ${board.title}</%def>
<div class="board-agreement sheet alternate">
    <div class="container">
        <h2 class="sheet-title">New topic</h2>
        % if board.agreements:
        <div class="sheet-body content">
            ${formatters.format_markdown(request, board.agreements)}
        </div>
        % endif
        <div class="board-agreement-notice sheet-body">
            <p>
                By posting, you are agree to the website's terms of use and usage agreements. The website reserve all rights at its discretion, to change, modify, add, or remove any content, as well as deny, or restrict access to the website. <strong>Press a back button now</strong> if you do not agree.
            </p>
        </div>
    </div>
</div>
<div class="sheet">
    <div class="sheet-body">
        <div class="container">
            <form class="form" action="${request.route_path('board_new', board=board.slug)}" method="post">
                <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
                <div class="form-item${' error' if form.title.errors else ''}">
                    <label class="form-item-label" for="${form.title.id}">Topic</label>
                    ${form.title(class_="input block font-large")}
                    % if form.title.errors:
                        <span class="form-item-error">${form.title.errors[0]}</span>
                    % endif
                </div>
                <div class="form-item${' error' if form.body.errors else ''}">
                    <label class="form-item-label" for="${form.body.id}">Body</label>
                    ${form.body(class_="input block font-content", rows=6)}
                    % if form.body.errors:
                        <span class="form-item-error">${form.body.errors[0]}</span>
                    % endif
                </div>
                <div class="form-item">
                    <button class="button brand" type="submit">New Topic</button>
                </div>
            </form>
        </div>
    </div>
</div>
