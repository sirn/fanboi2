<%inherit file='../_layout.mako' />
<%def name='title()'>Pages - Admin Panel</%def>
<%def name='subheader_title()'>Pages</%def>
<%def name='subheader_body()'>Manage pages.</%def>
<h2 class="sheet-title">${page_slug}</h2>
<%include file='_nav.mako' />
<div class="sheet-body">
    <form class="form" action="${request.route_path('admin_page_internal_edit', page=page_slug)}" method="post">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="form-item${' error' if form.body.errors else ''}">
            <label class="form-item-label" for="${form.body.id}">Body</label>
            ${form.body(class_="input block font-content font-monospaced", rows=6)}
            % if form.body.errors:
                <span class="form-item-error">${form.body.errors[0]}</span>
            % endif
        </div>
        <div class="form-item">
            % if page:
                <button class="btn btn--shadowed btn--brand" type="submit">Update Internal Page</button>
            % else:
                <button class="btn btn--shadowed btn--brand" type="submit">Create Internal Page</button>
            % endif
        </div>
    </form>
</div>
