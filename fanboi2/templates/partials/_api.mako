<%def name="render_api(name, title, method=None)">
    <div id="${name}">
        <div class="panel panel--shade2">
            <div class="container u-pd-vertical-l">
                <div class="flex flex--column flex--gap-m">
                    <div class="panel__item flex__item">
                        <div class="u-txt-s"><a href="#${name}">#${name}</a></div>
                        <h2 class="u-mg-reset u-txt-brand${' u-mg-bottom-s' if method and hasattr(caller, 'path') else ''}">${title}</h2>
                        % if method and hasattr(caller, 'path'):
                            <div class="u-txt-gray4"><strong class="${'u-txt-pill-primary' if method == 'GET' else 'u-txt-pill-danger'} u-txt-s">${method}</strong> ${caller.path()}</div>
                        % endif
                    </div>
                    % if hasattr(caller, 'description'):
                        <div class="panel__item flex__item u-scrollable u-txt-rich">
                            ${caller.description()}
                        </div>
                    % endif
                    % if hasattr(caller, 'request_query'):
                        <div class="panel__item flex__item">
                            <h3 class="u-txt-gray4">Query String</h3>
                            <div class="u-scrollable u-txt-rich">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Query</th>
                                            <th>Description</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${caller.request_query()}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    % endif
                    % if hasattr(caller, 'request_body'):
                        <div class="panel__item flex__item">
                            <h3 class="u-txt-gray4">Request</h3>
                            <div class="u-scrollable u-txt-rich">
                                ${caller.request_body()}
                            </div>
                        </div>
                    % endif
                    % if hasattr(caller, 'request_object'):
                        <div class="panel__item flex__item">
                            <h3 class="u-txt-gray4">Request Object</h3>
                            <div class="u-scrollable u-txt-rich">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Field</th>
                                            <th>Type</th>
                                            <th>Description</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${caller.request_object()}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    % endif
                </div>
            </div>
        </div>
        <div class="panel panel--shade3">
            <div class="container u-pd-vertical-l">
                <div class="flex flex--column flex--gap-m">
                    % if hasattr(caller, 'response_body'):
                        <div class="panel__item flex__item">
                            <h3 class="u-txt-gray4">Response</h3>
                            <div class="u-scrollable u-txt-rich">
                                ${caller.response_body()}
                            </div>
                        </div>
                    % endif
                    % if hasattr(caller, 'response_object'):
                        <div class="panel__item flex__item">
                            <h3 class="u-txt-gray4">Response Object</h3>
                            <div class="u-scrollable u-txt-rich">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Field</th>
                                            <th>Type</th>
                                            <th>Description</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${caller.response_object()}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    % endif
                </div>
            </div>
        </div>
    </div>
</%def>
