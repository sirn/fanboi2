<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%namespace name='datetime' file='../../partials/_datetime.mako' />
<%inherit file='../_layout.mako' />
<%def name='title()'>Pages - Admin Panel</%def>
<%def name='subheader_title()'>Pages</%def>
<%def name='subheader_body()'>Manage pages.</%def>
<h2 class="sheet-title">${page.title}</h2>
<%include file='_nav.mako' />
<div class="sheet-body">
    <table class="admin-table">
        <tbody class="admin-table-body">
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Slug</th>
                <td class="admin-table-item">
                    <a href="${request.route_path('page', page=page.slug)}">${page.slug}</a>
                </td>
            </tr>
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Title</th>
                <td class="admin-table-item">
                    ${page.title}
                </td>
            </tr>
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
        </tbody>
    </table>
</div>
<div class="sheet-body content">
    <div class="admin-embed">
        ${formatters.format_page(request, page)}
    </div>
</div>
<div class="sheet-body">
    <a class="btn btn--shadowed btn--brand" href="${request.route_path('admin_page_edit', page=page.slug)}">Edit Public Page</a>
    <a class="btn btn--shadowed" href="${request.route_path('admin_page_delete', page=page.slug)}">Delete Public Page</a>
</div>
