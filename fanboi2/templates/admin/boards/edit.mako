<%namespace name="nav" file="_nav.mako"/>
<%inherit file="../_layout.mako" />
<%def name="title()">Boards - Admin Panel</%def>
<%nav:render_nav title="${board.title}" board="${board}" />
<div class="sheet-body">
    <form class="form" action="${request.route_path('admin_board_edit', board=board.slug)}" method="post">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="form-item${' error' if form.title.errors else ''}">
            <label class="form-item-label" for="${form.title.id}">Title</label>
            ${form.title(class_="input block font-large")}
            % if form.title.errors:
                <span class="form-item-error">${form.title.errors[0]}</span>
            % endif
        </div>
        <div class="form-item${' error' if form.status.errors else ''}">
            <label class="form-item-label" for="${form.status.id}">Status</label>
            ${form.status()}
            % if form.status.errors:
                <span class="form-item-error">${form.status.errors[0]}</span>
            % endif
        </div>
        <div class="form-item${' error' if form.description.errors else ''}">
            <label class="form-item-label" for="${form.description.id}">Description</label>
            ${form.description(class_="input block font-large")}
            % if form.description.errors:
                <span class="form-item-error">${form.description.errors[0]}</span>
            % endif
        </div>
        <div class="form-item${' error' if form.agreements.errors else ''}">
            <label class="form-item-label" for="${form.agreements.id}">Agreements</label>
            ${form.agreements(class_="input block font-content font-monospaced", rows=6)}
            % if form.agreements.errors:
                <span class="form-item-error">${form.agreements.errors[0]}</span>
            % endif
        </div>
        <div class="form-item${' error' if form.settings.errors else ''}">
            <label class="form-item-label" for="${form.settings.id}">Settings</label>
            ${form.settings(class_="input block font-content font-monospaced", rows=6)}
            % if form.settings.errors:
                <span class="form-item-error">${form.settings.errors[0]}</span>
            % endif
        </div>
        <div class="form-item">
            <button class="btn btn--shadowed btn--brand" type="submit">Update Board</button>
        </div>
    </form>
</div>
