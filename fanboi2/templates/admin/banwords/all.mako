<%namespace name="datetime" file="../../partials/_datetime.mako" />
<%namespace name="nav" file="_nav.mako"/>
<%inherit file="../_layout.mako" />
<%def name="title()">Banwords - Admin Panel</%def>
<%nav:render_nav title="All Banwords" />
<div class="panel">
    <div class="panel__item u-scrollable">
        <table class="table">
            <thead>
                <tr>
                    <th>Expression</th>
                    <th>Scope</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                % for banword in banwords:
                    <tr>
                        <td>
                            <code><a href="${request.route_path('admin_banword', banword=banword.id)}">${banword.expr}</a></code>
                        </td>
                        <td>
                            % if banword.scope:
                                ${banword.scope}
                            % else:
                                <em>Global</em>
                            % endif
                        </td>
                        <td>
                            % if banword.description:
                                ${banword.description}
                            % else:
                                <em>No description</em>
                            % endif
                        </td>
                    </tr>
                % endfor
            </tbody>
        </table>
    </div>
</div>
