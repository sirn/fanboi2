<%def name="render_subheader(title, href=None)">
    <section class="panel panel--brand-dark">
        <div class="container u-pd-vertical-l">
            <h2 class="panel__item u-txt-center-mobile${' u-txt-light' if not href else ''}">
                % if href:
                    <a class="u-txt-light" href="${href}">${title}</a>
                % else:
                    ${title}
                % endif
            </h2>
            % if hasattr(caller, 'description'):
                <div class="panel__item u-txt-center-mobile u-txt-s u-txt-muted${' u-mg-bottom-s' if hasattr(caller, 'buttons') else ''}">${caller.description()}</div>
            % endif
            % if hasattr(caller, 'buttons'):
                <div class="panel__item">
                    <ul class="list flex flex--row flex--gap-xs u-center-mobile">
                        ${caller.buttons()}
                    </ul>
                </div>
            % endif
        </div>
    </section>
</%def>
<%def name="render_button(label, href, route_name=None, extra_class=None)">
    <li class="list__item flex__item"><a class="btn btn--shadowed btn--shadowed-dark${' btn--brand' if request.route_name == route_name else ' btn--dark' if route_name else ''}${' ' + extra_class if extra_class else ''}" href="${href}">${label}</a></li>
</%def>
