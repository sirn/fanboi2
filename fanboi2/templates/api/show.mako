<%inherit file='../partials/_layout.mako' />
<%def name='title()'>API documentation</%def>
<header class="subheader">
    <div class="container">
        <h2 class="subheader-title">API documentation</h2>
        <div class="subheader-body"><p>Reference for programmatic access of board data.</p></div>
    </div>
</header>
<%include file='_boards.mako' />
<%include file='_topics.mako' />
<%include file='_posts.mako' />
