<%namespace name='ident' file='../partials/_ident.mako' />
<%namespace name='datetime' file='../partials/_datetime.mako' />
<%inherit file='_layout.mako' />
<%def name='title()'>Dashboard - Admin Panel</%def>
<%def name='subheader_title()'>Dashboard</%def>
<%def name='subheader_body()'>Manage various aspect of the site.</%def>
<h2 class="sheet-title">Dashboard</h2>
<div class="sheet-body">
    <a class="button brand" href="${request.route_path('admin_logout')}">Logout</a>
</div>
<div class="sheet-body">
    <p>Logged in as <strong>${user.name}</strong> with ident <strong>${ident.render_ident(user.ident, user.ident_type)}</strong></p>
    <table class="admin-table">
        <thead class="admin-table-header">
            <tr class="admin-table-row">
                <th class="admin-table-item title">IP address</th>
                <th class="admin-table-item title sublead">Last seen at</th>
            </tr>
        </thead>
        <tbody class="admin-table-body">
            % for session in sessions:
            <tr class="admin-table-row">
                <td class="admin-table-item title">${session.ip_address}</td>
                <td class="admin-table-item sublead">${datetime.render_datetime(session.last_seen_at)}</td>
            </tr>
            % endfor
        </tbody>
    </table>
</div>
