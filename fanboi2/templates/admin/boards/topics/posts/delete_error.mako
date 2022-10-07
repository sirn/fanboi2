<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="nav" file="../_nav.mako"/>
<%inherit file="../../../_layout.mako" />
<%def name="title()">${board.title} - Admin Panel</%def>
<%nav:render_nav title="${topic.title}" board="${board}" />
<% num_posts = len(posts) %>
<h2 class="sheet-title">Error</h2>
<div class="sheet-body">
    <p>Posts containing the first post cannot be deleted.</p>
    <p>You may change the scope or <a href="${request.route_path('admin_board_topic_delete', board=board.slug, topic=topic.id)}">delete the topic</a> instead.</p>
</div>
<div class="sheet-body">
    <a class="btn btn--shadowed" href="${request.route_path('admin_board_topic', board=board.slug, topic=topic.id)}">Cancel</a>
</div>
