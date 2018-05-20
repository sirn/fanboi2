<%namespace name='datetime' file='../../partials/_datetime.mako' />
<%inherit file='../_layout.mako' />
<%def name='title()'>Bans - Admin Panel</%def>
<%def name='subheader_title()'>Bans</%def>
<%def name='subheader_body()'>Manage IP bans.</%def>
<h2 class="sheet-title">Inactive Bans</h2>
<%include file='_nav.mako' />
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
                    ${datetime.render_datetime(ban.active_until)}
                    % if ban.duration == 1:
                        (1 day)
                    % else:
                        (${ban.duration} days)
                    % endif
                % else:
                    <em>Indefinite</em>
                % endif
                </td>
            </tr>
            % endfor
        </tbody>
    </table>
</div>