<%namespace name='datetime' file='../../../partials/_datetime.mako' />
<%inherit file='../../_layout.mako' />
<%def name='title()'>${board.title} - Admin Panel</%def>
<%def name='subheader_title()'>Topics</%def>
<%def name='subheader_body()'>Manage topics.</%def>
<h2 class="sheet-title">${board.title}</h2>
<%include file='_nav.mako' />
% for topic in topics:
<div class="admin-cascade">
    <div class="admin-cascade-header">
        % if topic.status == 'locked':
        Locked:
        % elif topic.status == 'archived':
        Archived:
        % endif
        <strong><a href="${request.route_path('admin_board_topic_posts', board=board.slug, topic=topic.id, query='recent')}">${topic.title}</a></strong>
    </div>
    <div class="admin-cascade-body">
        <p>Last updated ${datetime.render_datetime(topic.meta.posted_at)}</p>
        <p>Total of <strong>${topic.meta.post_count} posts</strong></p>
    </div>
</div>
% endfor