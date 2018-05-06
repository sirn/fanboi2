<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%inherit file='../_layout.mako' />
<%def name='title()'>Bans - Admin Panel</%def>
<%def name='subheader_title()'>Bans</%def>
<%def name='subheader_body()'>Manage IP bans.</%def>
<div class="sheet-body">
    <a class="button green" href="${request.route_path('admin_ban_new')}">New Ban</a>
    <a class="button muted" href="${request.route_path('admin_bans')}">Active Bans</a>
</div>
<div class="sheet-body">
    <table class="admin-table">
        <thead class="admin-table-header">
            <tr class="admin-table-row">
                <th class="admin-table-item title">IP address</th>
                <th class="admin-table-item title sublead">Scope</th>
                <th class="admin-table-item title tail">Active until</th>
            </tr>
        </thead>
        <tbody class="admin-table-body">
            % for ban in bans:
            <tr class="admin-table-row">
                <th class="admin-table-item title"><a href="${request.route_path('admin_ban', ban=ban.id)}">${ban.ip_address}</a></th>
                <td class="admin-table-item">
                % if ban.scope:
                    ${ban.scope}
                % else:
                    <em>Global</em>
                % endif
                </td>
                <td class="admin-table-item">
                % if ban.active_until:
                    ${formatters.format_datetime(request, ban.active_until)}
                % else:
                    <em>Indefinite</em>
                % endif
                </td>
            </tr>
            % endfor
        </tbody>
    </table>
</div>