<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%inherit file='../_layout.mako' />
<%def name='title()'>Bans - Admin Panel</%def>
<%def name='subheader_title()'>Bans</%def>
<%def name='subheader_body()'>Manage IP bans.</%def>
<h2 class="sheet-title">${ban.ip_address}</h2>
<%include file='_nav.mako' />
<div class="sheet-body">
    <table class="admin-table">
        <tbody class="admin-table-body">
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">IP address</th>
                <td class="admin-table-item">
                    ${ban.ip_address}
                    % if not ban.active:
                        — <strong>Inactive</strong>
                    % endif
                </td>
            </tr>
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Description</th>
                <td class="admin-table-item">
                % if ban.description:
                    ${ban.description}
                % else:
                    <em>No description</em>
                % endif
                </td>
            </tr>
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Active until</th>
                <td class="admin-table-item">
                % if ban.active_until:
                    ${formatters.format_datetime(request, ban.active_until)}
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
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Scope</th>
                <td class="admin-table-item">
                % if ban.scope:
                    ${ban.scope}
                % else:
                    <em>Global</em>
                % endif
                </td>
            </tr>
        </tbody>
    </table>
    <a class="button brand" href="${request.route_path('admin_ban_edit', ban=ban.id)}">Edit Ban</a>
</div>