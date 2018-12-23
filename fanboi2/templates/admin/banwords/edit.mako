<%inherit file='../_layout.mako' />
<%def name='title()'>Banwords - Admin Panel</%def>
<%def name='subheader_title()'>Banwords</%def>
<%def name='subheader_body()'>Manage banwords.</%def>
<h2 class="sheet-title">${banword.expr}</h2>
<%include file='_nav.mako' />
<form class="form noshade" action="${request.route_path('admin_banword_edit', banword=banword.id)}" method="post">
    <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
    <div class="form-item${' error' if form.expr.errors else ''}">
        <label class="form-item-label" for="${form.expr.id}">Expression</label>
        ${form.expr(class_="input block font-large font-monospaced")}
        % if form.expr.errors:
            <span class="form-item-error">${form.expr.errors[0]}</span>
        % endif
    </div>
    <div class="form-item${' error' if form.description.errors else ''}">
        <label class="form-item-label" for="${form.description.id}">Description</label>
        ${form.description(class_="input block font-large")}
        % if form.description.errors:
            <span class="form-item-error">${form.description.errors[0]}</span>
        % endif
    </div>
    <div class="form-item${' error' if form.scope.errors else ''}">
        <label class="form-item-label" for="${form.scope.id}">Scope</label>
        ${form.scope(class_="input block font-large")}
        % if form.scope.errors:
            <span class="form-item-error">${form.scope.errors[0]}</span>
        % endif
    </div>
    <div class="form-item">
        <button class="button brand" type="submit">Update Banword</button>
        <span class="form-item-inline">
            ${form.active()} <label for="${form.active.id}">${form.active.label.text}</label>
        </span>
    </div>
</form>
