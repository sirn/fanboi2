<%namespace name="subheader" file="partials/_subheader.mako" />
<%inherit file="partials/_layout.mako" />
<%def name="title()">Bad Request</%def>
<%subheader:render_subheader title="400 Bad Request">
    <%def name="description()">
        <p>The request is invalid.</p>
    </%def>
</%subheader:render_subheader>
<div class="panel">
    <div class="container flex flex--column flex--gap-xs u-pd-vertical-xl">
        <h2 class="panel__item plex__item u-txt-brand">I will take the ring to Mordor.</h2>
        <p class="panel__item plex__item">Though I do not know the way.</p>
        <p class="panel__item plex__item"><em>Please retry the previous operation.</em></p>
    </div>
</div>
