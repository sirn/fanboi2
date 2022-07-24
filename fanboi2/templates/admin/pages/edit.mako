<%inherit file='../_layout.mako' />
<%def name='title()'>Pages - Admin Panel</%def>
<%def name='subheader_title()'>Pages</%def>
<%def name='subheader_body()'>Manage pages.</%def>
<h2 class="sheet-title">${page.title}</h2>
<%include file='_nav.mako' />
<div class="sheet-body">
    <form class="form" action="${request.route_path('admin_page_edit', page=page.slug)}" method="post">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="form-item${' error' if form.title.errors else ''}">
            <label class="form-item-label" for="${form.title.id}">Title</label>
            ${form.title(class_="input block font-large")}
            % if form.title.errors:
                <span class="form-item-error">${form.title.errors[0]}</span>
            % endif
        </div>
        <div class="form-item${' error' if form.body.errors else ''}">
            <label class="form-item-label" for="${form.body.id}">Body</label>
            ${form.body(class_="input block font-content font-monospaced", rows=6)}
            % if form.body.errors:
                <span class="form-item-error">${form.body.errors[0]}</span>
            % endif
        </div>
        <div class="form-item">
            <button class="button brand" type="submit">Update Public Page</button>
        </div>
    </form>
</div>
