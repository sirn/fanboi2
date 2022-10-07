<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%include file="_subheader.mako" />
<%inherit file="../partials/_layout.mako" />
<%def name='title()'>${page.title}</%def>
<div class="panel">
    <div class="container u-pd-vertical-xl">
         <div class="u-txt-rich u-scrollable">
              ${formatters.format_page(request, page)}
         </div>
    </div>
</div>
