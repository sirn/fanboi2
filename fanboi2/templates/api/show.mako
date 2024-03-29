<%inherit file='../partials/_layout.mako' />
<%def name='title()'>API documentation</%def>
<header class="subheader">
    <div class="container">
        <h2 class="subheader-title">API documentation</h2>
        <div class="subheader-body"><p>Last updated <strong><time datetime="2022-08-14">April 14, 2022</time></strong></p></div>
    </div>
</header>
<%include file='_boards.mako' />
<%include file='_topics.mako' />
<%include file='_posts.mako' />
<%include file='_pages.mako' />
<%include file='_other.mako' />
