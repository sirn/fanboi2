<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%inherit file='../_layout.mako' />
<%def name='title()'>Topics - Admin Panel</%def>
<%def name='subheader_title()'>Topics</%def>
<%def name='subheader_body()'>Manage topics.</%def>
<h2 class="sheet-title">All Topics</h2>
<%include file='_nav.mako' />
% for topic in topics:
<div class="admin-cascade">
    <div class="admin-cascade-header">
        <a href="${request.route_path('admin_topic', topic=topic.id)}">${topic.title}</a></strong>
    </div>
    <div class="admin-cascade-body">
        <p>${topic.meta.post_count} posts in <a href="${request.route_path('admin_board', board=topic.board.slug)}">${topic.board.title}</a></p>
        <p>Last updated ${formatters.format_datetime(request, topic.meta.posted_at)}</p>
    </div>
</div>
% endfor