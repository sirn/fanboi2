<%namespace name="subheader" file="partials/_subheader.mako" />
<%inherit file="partials/_layout.mako" />
<%def name="title()">Not Found</%def>
<%subheader:render_subheader title="404 Not Found">
    <%def name="description()">
        <p>The page you requested could not be found.</p>
    </%def>
</%subheader:render_subheader>
<div class="panel">
    <div class="container flex flex--column flex--gap-xs u-pd-vertical-xl">
        <h2 class="panel__item plex__item u-txt-brand">There is insufficient data for a meaningful answer.</h2>
        <p class="panel__item plex__item">No problem is insoluble in all conceivable circumstances.</p>
        <p class="panel__item plex__item"><em>Either check the URL or the content may have been removed.</em></p>
    </div>
</div>
