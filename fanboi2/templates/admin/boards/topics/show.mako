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
<div class="sheet-body">
    <a class="button brand" href="${request.route_path('admin_board_topic_edit', board=board.slug, topic=topic.id)}">Edit Topic</a>
    <a class="button default" href="${request.route_path('admin_board_topic_delete', board=board.slug, topic=topic.id)}">Delete Topic</a>
</div>
% if posts:
    % if posts[0].number != 1:
    <div class="sheet-body">
        <a href="${request.route_path('admin_board_topic_posts', board=board.slug, topic=topic.id, query="1-%s" % posts[-1].number)}" class="button block muted">
        % if posts[0].number <= 2:
        Load post 1
        % else:
        Load posts 1-${posts[0].number - 1}
        % endif
        </a>
    </div>
    % endif
    % for post in posts:
    <div class="admin-cascade">
        <div class="admin-cascade-header">
            <span class="admin-post-info number${' bumped' if post.bumped else ''}">${post.number}</a></span>
            <span class="admin-post-info name">${post.name}</span>
            <time class="admin-post-info date">Posted ${formatters.format_datetime(request, post.created_at)}</time>
        </div>
        <div class="admin-cascade-body admin-post-body">
            ${formatters.format_post(request, post)}
        </div>
        <div class="admin-cascade-footer">
            <span class="admin-post-info ip-address">${post.ip_address}</span>
            % if post.ident:
            <span class="admin-post-info ident">ID:${post.ident}</span>
            % endif
            % if post.number != 1:
            <a href="${request.route_path('admin_board_topic_posts_delete', board=board.slug, topic=topic.id, query=post.number)}">Delete</a>
            % endif
        </div>
    </div>
    % endfor
    % if posts[-1].number != topic.meta.post_count:
    <div class="sheet-body">
        <a href="${request.route_path('admin_board_topic_posts', board=board.slug, topic=topic.id, query="%s-" % posts[0].number)}" class="button block muted">Load posts ${posts[-1].number + 1}-</a>
    </div>
    % endif
% endif
% if topic.status != 'archived' and board.status != 'archived':
<form class="form noshade" action="${request.route_path('admin_board_topic', board=board.slug, topic=topic.id)}" method="post">
    <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
    <div class="container">
        <div class="form-item${' error' if form.body.errors else ''}">
            <label class="form-item-label" for="${form.body.id}">Reply</label>
            ${form.body(class_='input block content', rows=4)}
            % if form.body.errors:
                <span class="form-item-error">${form.body.errors[0]}</span>
            % endif
        </div>
        <div class="form-item">
            <p>Posting as <strong>${user.name}</strong> with ident <strong>${user.ident}</strong></p>
            % if topic.status == 'locked':
            <p>Topic is currently <strong>locked</strong>. You can post, but other users won't be able to respond.</p>
            % elif board.status == 'locked':
            <p>Board is currently <strong>locked</strong>. You can post, but other users won't be able to respond.</p>
            % endif
        </div>
        <div class="form-item">
            <button class="button green" type="submit">Post Reply</button>
            <span class="form-item-inline">
                ${form.bumped} <label for="${form.bumped.id}">${form.bumped.label.text}</label>
            </span>
        </div>
    </div>
</form>
% endif