<%inherit file='../_layout.mako' />
<%def name='title()'>Bans - Admin Panel</%def>
<%def name='subheader_title()'>Bans</%def>
<%def name='subheader_body()'>Manage IP bans.</%def>
<h2 class="sheet-title">New Ban</h2>
<%include file='_nav.mako' />
<form class="form noshade" action="${request.route_path('admin_ban_new')}" method="post">
    <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
    <div class="form-item${' error' if form.ip_address.errors else ''}">
        <label class="form-item-label" for="${form.ip_address.id}">IP address</label>
        ${form.ip_address(class_="input block font-large")}
        % if form.ip_address.errors:
            <span class="form-item-error">${form.ip_address.errors[0]}</span>
        % endif
    </div>
    <div class="form-item${' error' if form.description.errors else ''}">
        <label class="form-item-label" for="${form.description.id}">Description</label>
        ${form.description(class_="input block font-large")}
        % if form.description.errors:
            <span class="form-item-error">${form.description.errors[0]}</span>
        % endif
    </div>
    <div class="form-item${' error' if form.duration.errors else ''}">
        <label class="form-item-label" for="${form.duration.id}">Duration</label>
        ${form.duration(class_="input block font-large")}
        % if form.duration.errors:
            <span class="form-item-error">${form.duration.errors[0]}</span>
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
        <button class="button green" type="submit">Create Ban</button>
        <span class="form-item-inline">
            ${form.active()} <label for="${form.active.id}">${form.active.label.text}</label>
        </span>
    </div>
</form>
