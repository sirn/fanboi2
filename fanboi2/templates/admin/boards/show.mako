<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%inherit file='../_layout.mako' />
<%def name='title()'>Boards - Admin Panel</%def>
<%def name='subheader_title()'>Boards</%def>
<%def name='subheader_body()'>Manage boards.</%def>
<h2 class="sheet-title">${board.title}</h2>
<%include file='_nav.mako' />
<div class="sheet-body">
    <table class="admin-table">
        <tbody class="admin-table-body">
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Slug</th>
                <td class="admin-table-item">
                    ${board.slug}
                </td>
            </tr>
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Title</th>
                <td class="admin-table-item">
                    ${board.title}
                </td>
            </tr>
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Status</th>
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
            </tr>
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Description</th>
                <td class="admin-table-item">
                    % if board.description:
                    ${board.description}
                    % else:
                    <em>No description</em>
                    % endif
                </td>
            </tr>
            <tr class="admin-table-row">
                <th class="admin-table-item title lead">Settings</th>
                <td class="admin-table-item"><pre class="codeblock noshade">${formatters.format_json(request, board.settings)}</pre></td>
            </tr>
        </tbody>
    </table>
</div>
<h2 class="sheet-title">Agreements</h2>
<div class="sheet-body content">
    % if board.agreements:
    <div class="admin-embed">
        ${formatters.format_markdown(request, board.agreements)}
    </div>
    % else:
    <p><em>No agreements</em></p>
    % endif
</div>
<div class="sheet-body">
    <a class="button brand" href="${request.route_path('admin_board_edit', board=board.slug)}">Edit Board</a>
</div>