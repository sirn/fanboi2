<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>${page.title}</%def>
<div class="panel util-padded">
    <div class="container">
        <div class="panel__item">
            ${formatters.format_page(request, page)}
        </div>
    </div>
</div>
