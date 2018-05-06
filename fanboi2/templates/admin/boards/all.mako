<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%inherit file='../_layout.mako' />
<%def name='title()'>Boards - Admin Panel</%def>
<%def name='subheader_title()'>Boards</%def>
<%def name='subheader_body()'>Manage boards.</%def>
<div class="sheet-body">
    <a class="button green" href="${request.route_path('admin_board_new')}">New Board</a>
</div>
<div class="sheet-body">
    <table class="admin-table">
        <thead class="admin-table-header">
            <tr class="admin-table-row">
                <th class="admin-table-item title">Title</th>
                <th class="admin-table-item title sublead">Status</th>
                <th class="admin-table-item title tail">Last updated</th>
            </tr>
        </thead>
        <tbody class="admin-table-body">
            % for board in boards:
            <tr class="admin-table-row">
                <th class="admin-table-item title"><a href="${request.route_path('admin_board', board=board.slug)}">${board.title}</a></th>
                <td class="admin-table-item">${board.status}</td>
                <td class="admin-table-item">${formatters.format_datetime(request, board.updated_at or board.created_at)}</td>
            </tr>
            % endfor
        </tbody>
    </table>
</div>