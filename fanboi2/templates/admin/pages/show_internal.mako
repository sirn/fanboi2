<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%namespace name='datetime' file='../../partials/_datetime.mako' />
<%inherit file='../_layout.mako' />
<%def name='title()'>Pages - Admin Panel</%def>
<%def name='subheader_title()'>Pages</%def>
<%def name='subheader_body()'>Manage pages.</%def>
<h2 class="sheet-title">${page_slug}</h2>
<%include file='_nav.mako' />
<div class="sheet-body">
    <table class="admin-table">
        <tbody class="admin-table-body">
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Slug</th>
                <td class="admin-table-item">${page_slug}</td>
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
% if page:
<div class="sheet-body content">
    <div class="admin-embed">
        <pre class="codeblock noshade">${page.body}</pre>
    </div>
</div>
<div class="sheet-body">
    <a class="button brand" href="${request.route_path('admin_page_internal_edit', page=page.slug)}">Edit Internal Page</a>
    <a class="button default" href="${request.route_path('admin_page_internal_delete', page=page.slug)}">Delete Internal Page</a>
</div>
% else:
<div class="sheet-body">
    <a class="button brand" href="${request.route_path('admin_page_internal_edit', page=page_slug)}">Create Internal Page</a>
</div>
% endif