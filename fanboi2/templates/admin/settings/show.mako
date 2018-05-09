<%inherit file='../_layout.mako' />
<%def name='title()'>Settings - Admin Panel</%def>
<%def name='subheader_title()'>Settings</%def>
<%def name='subheader_body()'>Manage site runtime settings.</%def>
<h2 class="sheet-title">${key}</h2>
<%include file='_nav.mako' />
<form class="form noshade" action="${request.route_path('admin_setting', setting=key)}" method="post">
    <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
    <div class="form-item${' error' if form.value.errors else ''}">
        <label class="form-item-label" for="${form.value.id}">Value</label>
        ${form.value(class_="input block font-content font-monospaced", rows=6)}
        % if form.value.errors:
            <span class="form-item-error">${form.value.errors[0]}</span>
        % endif
    </div>
    <div class="form-item">
        <button class="button brand" type="submit">Update Setting</button>
    </div>
</form>