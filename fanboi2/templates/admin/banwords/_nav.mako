<%def name="render_nav(title=None)">
    <div class="panel u-mg-bottom-m">
        % if title:
            <h2 class="panel__item u-txt-brand u-mg-bottom-s">${title}</h2>
        % endif
        <div class="panel__item">
            <ul class="list flex flex--row flex--gap-xs">
                <li class="list__item flex__item"><a class="btn btn--bordered btn--shadowed" href="${request.route_path('admin_banwords')}">Active Banwords</a></li>
                <li class="list__item flex__item"><a class="btn btn--bordered btn--shadowed" href="${request.route_path('admin_banwords_inactive')}">Inactive Banwords</a></li>
                <li class="list__item flex__item"><a class="btn btn--shadowed btn--primary" href="${request.route_path('admin_banword_new')}">New Banword</a></li>
            </ul>
        </div>
    </div>
</%def>
