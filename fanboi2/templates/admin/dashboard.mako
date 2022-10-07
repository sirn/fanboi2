<%namespace name='ident' file='../partials/_ident.mako' />
<%namespace name='datetime' file='../partials/_datetime.mako' />
<%inherit file='_layout.mako' />
<%def name='title()'>Dashboard - Admin Panel</%def>
<h2 class="panel__item u-txt-brand u-mg-bottom-m">Dashboard</h2>
<p class="panel__item u-mg-bottom-m">Logged in as <strong>${user.name}</strong> with ident <strong>${ident.render_ident(user.ident, user.ident_type)}</strong></p>
<div class="panel__item">
    <table class="table">
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
