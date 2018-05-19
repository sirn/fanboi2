<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%inherit file='../../../_layout.mako' />
<%def name='title()'>${board.title} - Admin Panel</%def>
<%def name='subheader_title()'>Topics</%def>
<%def name='subheader_body()'>Manage topics.</%def>
<h2 class="sheet-title">${topic.title}</h2>
<%include file='../_nav.mako' />
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
    </div>
</div>
% endfor
<h2 class="sheet-title">Delete confirmation</h2>
<div class="sheet-body">
    <p>
        <% num_posts = len(posts) %>
        Are you sure you want to delete a total of
        % if num_posts == 1:
        <strong>1 post</strong>?
        % else:
        <strong>${num_posts} posts</strong>?
        % endif
        This operation cannot be undone.
    </p>
</div>
<div class="sheet-body">
    <form class="form noshade" action="${request.route_path('admin_board_topic_posts_delete', board=board.slug, topic=topic.id, query=query)}" method="post">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <button class="button brand" type="submit">
            Delete
            % if num_posts == 1:
            Post
            % else:
            Posts
            % endif
        </button>
        <a class="button" href="${request.route_path('admin_board_topic', board=board.slug, topic=topic.id)}">Cancel</a>
    </form>
</div>