<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%namespace name='datetime' file='../../partials/_datetime.mako' />
<%inherit file='../_layout.mako' />
<%def name='title()'>Pages - Admin Panel</%def>
<%def name='subheader_title()'>Pages</%def>
<%def name='subheader_body()'>Manage pages.</%def>
<h2 class="sheet-title">${page.slug}</h2>
<%include file='_nav.mako' />
<div class="sheet-body">
    <table class="admin-table">
        <tbody class="admin-table-body">
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Slug</th>
                <td class="admin-table-item">${page.slug}</td>
            </tr>
            % if page:
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Namespace</th>
                <td class="admin-table-item">
                    ${page.namespace}
                </td>
            </tr>
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Formatter</th>
                <td class="admin-table-item">
                    ${page.formatter}
                </td>
            </tr>
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Last updated</th>
                <td class="admin-table-item">
                    ${datetime.render_datetime(page.updated_at or page.created_at)}
                </td>
            </tr>
            % else:
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Last updated</th>
                <td class="admin-table-item"><em>Not created</em></td>
            </tr>
            % endif
        </tbody>
    </table>
</div>
<h2 class="sheet-title">Delete confirmation</h2>
<div class="sheet-body">
    <p>Are you sure you want to delete internal page <strong>${page.title}</strong>? This operation cannot be undone.</p>
</div>
<div class="sheet-body">
    <form class="form" action="${request.route_path('admin_page_internal_delete', page=page.slug)}" method="post">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <button class="button brand" type="submit">Delete Internal Page</button>
        <a class="button" href="${request.route_path('admin_page_internal', page=page.slug)}">Cancel</a>
    </form>
</div>
