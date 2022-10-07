<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="formtpl" file="../partials/_form.mako" />
<%include file="_subheader.mako" />
<%inherit file="../partials/_layout.mako" />
<%def name="title()">New topic - ${board.title}</%def>
<div class="panel panel--shade2">
    <div class="container u-pd-vertical-l">
        <h2 class="panel__item u-txt-gray4 u-mg-bottom-s">New topic</h2>
        % if board.agreements:
        <div class="panel__item u-mg-bottom-s">
            ${formatters.format_markdown(request, board.agreements)}
        </div>
        % endif
        <div class="panel__item u-txt-s u-txt-gray4">
            <p>
                By posting, you are agree to the website's terms of use and usage agreements. The website reserve all rights at its discretion, to change, modify, add, or remove any content, as well as deny, or restrict access to the website. <strong>Press a back button now</strong> if you do not agree.
            </p>
        </div>
    </div>
</div>
<div class="panel panel--shade3">
    <div class="container u-pd-vertical-l">
        <div class="panel__item">
            <%formtpl:render_form href="${request.route_path('board_new', board=board.slug)}">
                <%formtpl:render_field form="${form}" field="title" />
                <%formtpl:render_field form="${form}" field="body" rows="10" />
                <%formtpl:render_button form="${form}" label="New Topic" color="brand" />
            </%formtpl:render_form>
        </div>
    </div>
</div>
