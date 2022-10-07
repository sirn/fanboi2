<%inherit file="../partials/_layout.mako" />
<%namespace name="subheader" file="../partials/_subheader.mako" />
<%namespace name="formtpl" file="../partials/_form.mako" />
<%def name='title()'>Login - Admin Panel</%def>
<%subheader:render_subheader title="Admin Panel">
    <%def name="description()">
        <p>Login is required beyond this point.</p>
    </%def>
</%subheader:render_subheader>
<div class="panel panel--shade3">
    <div class="container u-pd-vertical-l">
        <div class="panel__item">
            <%formtpl:render_form href="${request.route_path('admin_root')}">
                <%formtpl:render_field form="${form}" field="username" />
                <%formtpl:render_field form="${form}" field="password" />
                <%formtpl:render_button form="${form}" label="Login" color="brand" />
            </%formtpl:render_form>
        </div>
    </div>
</div>
