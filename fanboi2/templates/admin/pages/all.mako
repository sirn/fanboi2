<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%inherit file='../_layout.mako' />
<%def name='title()'>Pages - Admin Panel</%def>
<%def name='subheader_title()'>Pages</%def>
<%def name='subheader_body()'>Manage pages.</%def>
<h2 class="sheet-title">All Pages</h2>
<%include file='_nav.mako' />
<div class="sheet-body">
    <table class="admin-table">
        <thead class="admin-table-header">
            <tr class="admin-table-row">
                <th class="admin-table-item title">Public page</th>
                <th class="admin-table-item title tail">Last updated</th>
            </tr>
        </thead>
        <tbody class="admin-table-body">
            % for page in pages:
            <tr class="admin-table-row">
                <th class="admin-table-item title"><a href="${request.route_path('admin_page', page=page.slug)}">${page.slug}</a></th>
                <td class="admin-table-item">${formatters.format_datetime(request, page.updated_at or page.created_at)}</td>
            </tr>
            % endfor
        </tbody>
    </table>
</div>
<div class="sheet-body">
    <table class="admin-table">
        <thead class="admin-table-header">
            <tr class="admin-table-row">
                <th class="admin-table-item title">Internal page</th>
                <th class="admin-table-item title tail">Last updated</th>
            </tr>
        </thead>
        <tbody class="admin-table-body">
            % for page in pages_internal:
            <tr class="admin-table-row">
                <th class="admin-table-item title"><a href="${request.route_path('admin_page_internal', page=page.slug)}">${page.slug}</a></th>
                <td class="admin-table-item">
                % if page.created_at or page_updated_at:
                    ${formatters.format_datetime(request, page.updated_at or page.created_at)}
                % else:
                    <em>Not created</em>
                % endif
                </td>
            </tr>
            % endfor
        </tbody>
    </table>
</div>