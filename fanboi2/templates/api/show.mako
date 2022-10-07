<%namespace name="subheader" file="../partials/_subheader.mako" />
<%inherit file="../partials/_layout.mako" />
<%def name="title()">API documentation</%def>
<%subheader:render_subheader title="API documentation">
    <%def name="description()">
        <p>Last updated <strong><time datetime="2022-08-14">April 14, 2022</time></strong></p>
    </%def>
</%subheader:render_subheader>
<%include file="_boards.mako" />
<%include file="_topics.mako" />
<%include file="_posts.mako" />
<%include file="_pages.mako" />
<%include file="_other.mako" />
