<%namespace name="datetime" file="../../partials/_datetime.mako" />
<%namespace name="nav" file="_nav.mako" />
<%inherit file="../_layout.mako" />
<%def name="title()">Bans - Admin Panel</%def>
<%nav:render_nav title="${ban.ip_address}" />
<div class="panel">
    <div class="panel__item u-mg-bottom-m">
        <table class="table">
            <tbody>
                <tr>
                    <th>IP address</th>
                    <td>
                        ${ban.ip_address}
                        % if not ban.active:
                            — <strong>Inactive</strong>
                        % endif
                    </td>
                </tr>
                <tr>
                    <th>Description</th>
                    <td>
                        % if ban.description:
                            ${ban.description}
                        % else:
                            <em>No description</em>
                        % endif
                    </td>
                </tr>
                <tr>
                    <th>Active until</th>
                    <td>
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
                <tr>
                    <th>Scope</th>
                    <td>
                        % if ban.scope:
                            ${ban.scope}
                        % else:
                            <em>Global</em>
                        % endif
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <div class="panel__item">
        <a class="btn btn--shadowed btn--danger" href="${request.route_path('admin_ban_edit', ban=ban.id)}">Edit Ban</a>
    </div>
</div>
