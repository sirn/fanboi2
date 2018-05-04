<%inherit file='../partials/_layout.mako' />
<%def name='title()'>Login - Admin Panel</%def>
<header class="subheader">
    <div class="container">
        <h2 class="subheader-title">Admin Panel</h2>
        <div class="subheader-body"><p>Please perform initial setup.</p></div>
    </div>
</header>
<div class="sheet alternate">
    <div class="container">
        <h2 class="sheet-title">Initial setup</h2>
        <div class="sheet-body">
            <p>This instance of Fanboi2 installation hasn't been setup.</p>
            <p>The user created during this setup is considered a root user and can perform all operations.</p>
        </div>
    </div>
</div>
<form class="form" action="${request.route_path('admin_setup')}" method="post">
    <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
    <div class="container">
        <div class="form-item${' error' if form.username.errors else ''}">
            <label class="form-item-label" for="${form.username.id}">Username</label>
            ${form.username(class_="input block larger")}
            % if form.username.errors:
                <span class="form-item-error">${form.username.errors[0]}</span>
            % endif
        </div>
        <div class="form-item${' error' if form.password.errors else ''}">
            <label class="form-item-label" for="${form.password.id}">Password</label>
            ${form.password(class_="input block larger")}
            % if form.password.errors:
                <span class="form-item-error">${form.password.errors[0]}</span>
            % endif
        </div>
        <div class="form-item${' error' if form.password_confirm.errors else ''}">
            <label class="form-item-label" for="${form.password_confirm.id}">Password confirmation</label>
            ${form.password_confirm(class_="input block larger")}
            % if form.password_confirm.errors:
                <span class="form-item-error">${form.password_confirm.errors[0]}</span>
            % endif
        </div>
        <div class="form-item">
            <button class="button brand" type="submit">Create account</button>
        </div>
    </div>
</form>