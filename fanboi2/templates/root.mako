<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="subheader" file="partials/_subheader.mako" />
<%inherit file="partials/_layout.mako" />
<%subheader:render_subheader title="Welcome, stranger">
    <%def name="description()"><p>Please choose the board from the list below.</p></%def>
</%subheader:render_subheader>
% for board in boards:
    <div class="panel panel--separator panel--unit-link">
        <div class="container u-pd-vertical-l">
            <h3 class="panel__item">
                <a class="panel__link" href="${request.route_path('board', board=board.slug)}">${board.title}</a>
            </h3>
            <div class="panel__item u-txt-s u-txt-gray4">
                ${formatters.format_markdown(request, board.description)}
            </div>
        </div>
    </div>
% endfor
