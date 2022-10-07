<%def name="render_nav(title=None)">
    <div class="panel">
        % if title:
            <h2 class="panel__item u-txt-brand u-mg-bottom-s">${title}</h2>
        % endif
        <div class="panel__item u-mg-bottom-m">
            <ul class="list flex flex--row flex--gap-xs">
                <li class="list__item flex__item"><a class="btn btn--bordered btn--shadowed" href="${request.route_path('admin_bans')}">Active Bans</a></li>
                <li class="list__item flex__item"><a class="btn btn--bordered btn--shadowed" href="${request.route_path('admin_bans_inactive')}">Inactive Bans</a></li>
                <li class="list__item flex__item"><a class="btn btn--shadowed btn--primary" href="${request.route_path('admin_ban_new')}">New Ban</a></li>
            </ul>
        </div>
    </div>
</%def>
