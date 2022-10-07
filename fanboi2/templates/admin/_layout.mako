<%namespace name="subheader" file="../partials/_subheader.mako" />
<%inherit file="../partials/_layout.mako" />
<%subheader:render_subheader title="Admin">
    <%def name="description()">
        Welcome back
    </%def>
</%subheader:render_subheader>
<div class="container">
    <div class="flex flex--row flex--gap-m">
        <div class="flex__item">
            <div class="container u-pd-vertical-l">
                <h3 class="u-txt-gray4">My Actions</h3>
                <ul class="list u-mg-vertical-m">
                    <li class="list__item"><a href="${request.route_path('admin_dashboard')}">Dashboard</a></li>
                    <li class="list__item"><a href="${request.route_path('admin_logout')}">Logout</a></li>
                </ul>
                <h3 class="u-txt-gray4">Moderation</h3>
                <ul class="list u-mg-vertical-m">
                    <li class="list__item"><a href="${request.route_path('admin_bans')}">Bans</a></li>
                    <li class="list__item"><a href="${request.route_path('admin_banwords')}">Banwords</a></li>
                    <li class="list__item"><a href="${request.route_path('admin_boards')}">Boards</a></li>
                </ul>
                <h3 class="u-txt-gray4">System</h3>
                <ul class="list u-mg-vertical-m">
                    <li class="list__item"><a href="${request.route_path('admin_pages')}">Pages</a></li>
                    <li class="list__item"><a href="${request.route_path('admin_settings')}">Settings</a></li>
                </ul>
            </div>
        </div>
        <div class="flex__item flex__item--grow-2">
            <div class="container u-pd-vertical-l">
                ${next.body()}
            </div>
        </div>
    </div>
</div>
