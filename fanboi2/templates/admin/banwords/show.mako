<%namespace name="datetime" file="../../partials/_datetime.mako" />
<%namespace name="nav" file="_nav.mako" />
<%inherit file="../_layout.mako" />
<%def name="title()">Banwords - Admin Panel</%def>
<%nav:render_nav title="${banword.expr}" />
<div class="panel">
    <div class="panel__item u-mg-bottom-m">
        <table class="table">
            <tbody>
                <tr>
                    <th>Expression</th>
                    <td>
                        ${banword.expr}
                    </td>
                </tr>
                <tr>
                    <th>Description</th>
                    <td>
                        % if banword.description:
                            ${banword.description}
                        % else:
                            <em>No description</em>
                        % endif
                    </td>
                </tr>
                <tr>
                    <th>Scope</th>
                    <td>
                        % if banword.scope:
                            ${banword.scope}
                        % else:
                            <em>Global</em>
                        % endif
                    </td>
                </tr>
                <tr>
                    <th>Active</th>
                    <td>
                        % if banword.active:
                            Active
                        % else:
                            <strong>Inactive</strong>
                        % endif
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <div class="panel__item">
        <a class="btn btn--shadowed btn--danger" href="${request.route_path('admin_banword_edit', banword=banword.id)}">Edit Banword</a>
    </div>
</div>
