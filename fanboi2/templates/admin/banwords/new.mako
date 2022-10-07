<%namespace name="formtpl" file="_form.mako" />
<%namespace name="nav" file="_nav.mako" />
<%inherit file="../_layout.mako" />
<%def name="title()">Banwords - Admin Panel</%def>
<%nav:render_nav title="New Banword" />
<div class="panel">
    <div class="panel__item panel panel--gray1 panel--rounded u-pd-m">
        <div class="panel__item">
            <%formtpl:render_form form="${form}" href="${request.route_path('admin_banword_new')}" button_label="New Banword" button_color="primary" />
        </div>
    </div>
</div>
