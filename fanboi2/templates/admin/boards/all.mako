<%namespace name="datetime" file="../../partials/_datetime.mako" />
<%namespace name="nav" file="_nav.mako"/>
<%inherit file="../_layout.mako" />
<%def name="title()">Boards - Admin Panel</%def>
<%nav:render_nav title="All Boards" />
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
                <th class="admin-table-item title"><a href="${request.route_path('admin_board_topics', board=board.slug)}">${board.title}</a></th>
                <td class="admin-table-item">
                    % if board.status == 'open':
                    Open
                    % elif board.status == 'locked':
                    Locked
                    % elif board.status == 'restricted':
                    Restricted
                    % elif board.status == 'archived':
                    Archived
                    % endif
                </td>
                <td class="admin-table-item">${datetime.render_datetime(board.updated_at or board.created_at)}</td>
            </tr>
            % endfor
        </tbody>
    </table>
</div>
