<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%inherit file='../_layout.mako' />
<%def name='title()'>Settings - Admin Panel</%def>
<%def name='subheader_title()'>Settings</%def>
<%def name='subheader_body()'>Manage site runtime settings.</%def>
<h2 class="sheet-title">All Settings</h2>
<%include file='_nav.mako' />
<div class="sheet-body">
    <table class="admin-table">
        <thead class="admin-table-header">
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Key</th>
                <th class="admin-table-item title">Value</th>
            </tr>
        </thead>
        <tbody class="admin-table-body">
            % for key, value in settings:
            <tr class="admin-table-row">
                <th class="admin-table-item title"><a href="${request.route_path('admin_setting', setting=key)}">${key}</a></th>
                <td class="admin-table-item"><pre class="codeblock">${formatters.format_json(request, value)}</pre></td>
            </tr>
            % endfor
        </tbody>
    </table>
</div>
