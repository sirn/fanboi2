<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%inherit file='../../_layout.mako' />
<%def name='title()'>${board.title} - Admin Panel</%def>
<%def name='subheader_title()'>Topics</%def>
<%def name='subheader_body()'>Manage topics.</%def>
<h2 class="sheet-title">${topic.title}</h2>
<%include file='_nav.mako' />
<div class="sheet-body">
    <table class="admin-table">
        <tbody class="admin-table-body">
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Board</th>
                <td class="admin-table-item">${board.title}</td>
            </tr>
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Status</th>
                <td class="admin-table-item">
                    % if topic.status == 'open':
                    Open
                    % elif topic.status == 'locked':
                    Locked
                    % elif topic.status == 'archived':
                    Archived
                    % endif
                </td>
            </tr>
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Last posted</th>
                <td class="admin-table-item">
                    ${formatters.format_datetime(request, topic.meta.posted_at)}
                </td>
            </tr>
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Total posts</th>
                <td class="admin-table-item">
                    ${topic.meta.post_count}
                </td>
            </tr>
        </tbody>
    </table>
</div>
<h2 class="sheet-title">Delete confirmation</h2>
<div class="sheet-body">
    <p>Are you sure you want to delete topic <strong>${topic.title}</strong>? This operation cannot be undone.</p>
</div>
<div class="sheet-body">
    <form class="form noshade" action="${request.route_path('admin_board_topic_delete', board=board.slug, topic=topic.id)}" method="post">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <button class="button brand" type="submit">Delete Topic</button>
        <a class="button" href="${request.route_path('admin_board_topic', board=board.slug, topic=topic.id)}">Cancel</a>
    </form>
</div>