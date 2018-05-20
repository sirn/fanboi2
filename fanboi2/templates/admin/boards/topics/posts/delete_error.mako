<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%inherit file='../../../_layout.mako' />
<%def name='title()'>${board.title} - Admin Panel</%def>
<%def name='subheader_title()'>Topics</%def>
<%def name='subheader_body()'>Manage topics.</%def>
<h2 class="sheet-title">${topic.title}</h2>
<%include file='../_nav.mako' />
<% num_posts = len(posts) %>
<h2 class="sheet-title">Error</h2>
<div class="sheet-body">
    <p>Posts containing the first post cannot be deleted.</p>
    <p>You may change the scope or <a href="${request.route_path('admin_board_topic_delete', board=board.slug, topic=topic.id)}">delete the topic</a> instead.</p>
</div>
<div class="sheet-body">
    <a class="button" href="${request.route_path('admin_board_topic', board=board.slug, topic=topic.id)}">Cancel</a>
</div>