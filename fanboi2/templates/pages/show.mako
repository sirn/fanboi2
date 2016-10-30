<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>${page.title}</%def>
<div class="sheet">
    <div class="container">
         <div class="sheet-body">
              ${formatters.format_page(request, page)}
         </div>
    </div>
</div>