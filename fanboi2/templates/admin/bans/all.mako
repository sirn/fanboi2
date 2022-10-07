<%namespace name="datetime" file="../../partials/_datetime.mako" />
<%namespace name="nav" file="_nav.mako" />
<%inherit file="../_layout.mako" />
<%def name="title()">Bans - Admin Panel</%def>
<%nav:render_nav title="All Bans" />
<div class="panel">
    <div class="panel__item u-scrollable">
        <table class="table">
            <thead>
                <tr>
                    <th>IP address</th>
                    <th>Scope</th>
                    <th>Active until</th>
                </tr>
            </thead>
            <tbody>
                % for ban in bans:
                    <tr>
                        <td><a href="${request.route_path('admin_ban', ban=ban.id)}">${ban.ip_address}</a></td>
                        <td>
                            % if ban.scope:
                                ${ban.scope}
                            % else:
                                <em>Global</em>
                            % endif
                        </td>
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
                % endfor
            </tbody>
        </table>
    </div>
</div>
