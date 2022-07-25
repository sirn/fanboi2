<%inherit file='../partials/_layout.mako' />
<%def name='title()'>Login - Admin Panel</%def>
<header class="subheader">
    <div class="container">
        <h2 class="subheader-title">Admin Panel</h2>
        <div class="subheader-body"><p>Login is required beyond this point.</p></div>
    </div>
</header>
<div class="sheet">
    <div class="container">
        <div class="sheet-body">
            <form class="form" action="${request.route_path('admin_root')}" method="post">
                <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
                <div class="form-item${' error' if form.username.errors else ''}">
                    <label class="form-item-label" for="${form.username.id}">Username</label>
                    ${form.username(class_="input block font-large")}
                    % if form.username.errors:
                        <span class="form-item-error">${form.username.errors[0]}</span>
                    % endif
                </div>
                <div class="form-item${' error' if form.password.errors else ''}">
                    <label class="form-item-label" for="${form.password.id}">Password</label>
                    ${form.password(class_="input block font-large")}
                    % if form.password.errors:
                        <span class="form-item-error">${form.password.errors[0]}</span>
                    % endif
                </div>
                <div class="form-item">
                    <button class="button brand" type="submit">Login</button>
                </div>
            </form>
        </div>
    </div>
</div>
