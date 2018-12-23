<%namespace name='datetime' file='../../partials/_datetime.mako' />
<%inherit file='../_layout.mako' />
<%def name='title()'>Banwords - Admin Panel</%def>
<%def name='subheader_title()'>Banwords</%def>
<%def name='subheader_body()'>Manage banwords.</%def>
<h2 class="sheet-title">All Banwords</h2>
<%include file='_nav.mako' />
<div class="sheet-body">
    <table class="admin-table">
        <thead class="admin-table-header">
            <tr class="admin-table-row">
                <th class="admin-table-item title">Expression</th>
                <th class="admin-table-item title sublead">Scope</th>
                <th class="admin-table-item title tail">Description</th>
            </tr>
        </thead>
        <tbody class="admin-table-body">
            % for banword in banwords:
                <tr class="admin-table-row">
                    <th class="admin-table-item title">
                        <code><a href="${request.route_path('admin_banword', banword=banword.id)}">${banword.expr}</a></code>
                    </th>
                    <td class="admin-table-item">
                        % if banword.scope:
                            ${banword.scope}
                        % else:
                            <em>Global</em>
                        % endif
                    </td>
                    <td class="admin-table-item">
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
