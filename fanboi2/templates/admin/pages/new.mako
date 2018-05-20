<%inherit file='../_layout.mako' />
<%def name='title()'>Pages - Admin Panel</%def>
<%def name='subheader_title()'>Pages</%def>
<%def name='subheader_body()'>Manage pages.</%def>
<h2 class="sheet-title">New Public Page</h2>
<%include file='_nav.mako' />
<form class="form noshade" action="${request.route_path('admin_page_new')}" method="post">
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
    <div class="form-item${' error' if form.body.errors else ''}">
        <label class="form-item-label" for="${form.body.id}">Body</label>
        ${form.body(class_="input block font-large", rows=6)}
        % if form.body.errors:
            <span class="form-item-error">${form.body.errors[0]}</span>
        % endif
    </div>
    <div class="form-item">
        <button class="button green" type="submit">Create Public Page</button>
    </div>
</form>