<%namespace name="formatters" module="fanboi2.formatters" />
<%inherit file="../partials/_layout.mako" />
<%include file="_header.mako" />
<%def name="title()">New topic - ${board.title}</%def>
<header class="subheader-board">
    <div class="container">
        <h3 class="title">New topic</h3>
        ${formatters.format_markdown(request, board.agreements)}
        <p class="description">By continuing, you are agree to the above agreement. Otherwise, you may go back now.</p>
        <a class="button button-back" href="${request.route_path('board', board=board.slug)}">Back</a>
    </div>
</header>
<div id="new" class="new-topic">
    <div class="container">
        <form action="${request.route_path('board_new', board=board.slug)}" method="post" class="form">
            ${form.csrf_token}
            <div class="form-field${' form-error' if form.title.errors else ''}">
                <label for="${form.title.id}">Topic</label>
                ${form.title}
                % if form.title.errors:
                    <span class="error-message">${form.title.errors[0]}</span>
                % endif
            </div>
            <div class="form-field${' form-error' if form.body.errors else ''}">
                <label for="${form.body.id}">Body</label>
                ${form.body}
                % if form.body.errors:
                    <span class="error-message">${form.body.errors[0]}</span>
                % endif
            </div>
            <div class="form-actions">
                <button type="submit" class="button button-post">New Topic</button>
            </div>
        </form>
    </div>
</div>
