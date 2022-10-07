<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="datetime" file="../../../../partials/_datetime.mako" />
<%namespace name="ident" file="../../../../partials/_ident.mako" />
<%namespace name="nav" file="../_nav.mako"/>
<%inherit file="../../../_layout.mako" />
<%def name="title()">${board.title} - Admin Panel</%def>
<%nav:render_nav title="${topic.title}" board="${board}" />
% for post in posts:
<div class="admin-cascade">
    <div class="admin-cascade-header">
        <span class="admin-post-info number${' bumped' if post.bumped else ''}">${post.number}</a></span>
        <span class="admin-post-info name">${post.name}</span>
        <time class="admin-post-info date">Posted ${datetime.render_datetime(post.created_at)}</time>
    </div>
    <div class="admin-cascade-body admin-post-body">
        ${formatters.format_post(request, post)}
    </div>
    <div class="admin-cascade-footer">
        <span class="admin-post-info ip-address">${post.ip_address}</span>
        % if post.ident:
            <span class="admin-post-info ident">ID:${ident.render_ident(post.ident, post.ident_type)}</span>
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
    <form class="form" action="${request.route_path('admin_board_topic_posts_delete', board=board.slug, topic=topic.id, query=query)}" method="post">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <button class="btn btn--shadowed btn--brand" type="submit">
            Delete
            % if num_posts == 1:
            Post
            % else:
            Posts
            % endif
        </button>
        <a class="btn btn--shadowed" href="${request.route_path('admin_board_topic', board=board.slug, topic=topic.id)}">Cancel</a>
    </form>
</div>
