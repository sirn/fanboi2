<%namespace name="subheader" file="../partials/_subheader.mako" />
<%namespace name="datetime" file="../partials/_datetime.mako" />
<%subheader:render_subheader title="${page.title}" href="${request.route_path('page', page=page.slug)}">
    <%def name="description()">
        <p>Updated <strong>${datetime.render_datetime(page.updated_at or page.created_at)}</strong></p>
    </%def>
</%subheader:render_subheader>
