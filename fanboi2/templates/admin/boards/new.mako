<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%inherit file='../_layout.mako' />
<%def name='title()'>Boards - Admin Panel</%def>
<%def name='subheader_title()'>Boards</%def>
<%def name='subheader_body()'>Manage boards.</%def>
<h2 class="sheet-title">New Board</h2>
<%include file='_nav.mako' />
<form class="form noshade" action="${request.route_path('admin_board_new')}" method="post">
    <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
    <div class="form-item${' error' if form.slug.errors else ''}">
        <label class="form-item-label" for="${form.slug.id}">Slug</label>
        ${form.slug(class_="input block font-large")}
        % if form.slug.errors:
            <span class="form-item-error">${form.slug.errors[0]}</span>
        % endif
    </div>
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
        ${form.agreements(class_="input block font-large font-monospaced", rows=6)}
        % if form.agreements.errors:
            <span class="form-item-error">${form.agreements.errors[0]}</span>
        % endif
    </div>
    <div class="form-item${' error' if form.settings.errors else ''}">
        <label class="form-item-label" for="${form.settings.id}">Settings</label>
        ${form.settings(class_="input block font-large font-monospaced", rows=6)}
        % if form.settings.errors:
            <span class="form-item-error">${form.settings.errors[0]}</span>
        % endif
    </div>
    <div class="form-item">
        <button class="button green" type="submit">Create Board</button>
    </div>
</form>