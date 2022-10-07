<%namespace name="formtpl" file="_form.mako" />
<%namespace name="nav" file="_nav.mako" />
<%inherit file="../_layout.mako" />
<%def name="title()">Bans - Admin Panel</%def>
<%nav:render_nav title="${ban.ip_address}" />
<div class="panel">
    <div class="panel__item panel panel--gray1 panel--rounded u-pd-m">
        <div class="panel__item">
            <%formtpl:render_form form="${form}" href="${request.route_path('admin_ban_edit', ban=ban.id)}" button_label="Update Ban" button_color="danger" />
        </div>
    </div>
</div>
