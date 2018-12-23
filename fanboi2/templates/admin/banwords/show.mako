<%namespace name='datetime' file='../../partials/_datetime.mako' />
<%inherit file='../_layout.mako' />
<%def name='title()'>Banwords - Admin Panel</%def>
<%def name='subheader_title()'>Banwords</%def>
<%def name='subheader_body()'>Manage banwords.</%def>
<h2 class="sheet-title">${banword.expr}</h2>
<%include file='_nav.mako' />
<div class="sheet-body">
    <table class="admin-table">
        <tbody class="admin-table-body">
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Expression</th>
                <td class="admin-table-item">
                    ${banword.expr}
                    % if not banword.active:
                        — <strong>Inactive</strong>
                    % endif
                </td>
            </tr>
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Description</th>
                <td class="admin-table-item">
                % if banword.description:
                    ${banword.description}
                % else:
                    <em>No description</em>
                % endif
                </td>
            </tr>
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Scope</th>
                <td class="admin-table-item">
                % if banword.scope:
                    ${banword.scope}
                % else:
                    <em>Global</em>
                % endif
                </td>
            </tr>
        </tbody>
    </table>
    <a class="button brand" href="${request.route_path('admin_banword_edit', banword=banword.id)}">Edit Banword</a>
</div>
