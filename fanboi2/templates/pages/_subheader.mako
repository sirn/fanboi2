<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<header class="subheader">
    <div class="container">
        <h2 class="subheader-title"><a href="${request.route_path('page', page=page.slug)}">${page.title}</a></h2>
        <div class="subheader-body lines">Updated <strong>${formatters.format_datetime(request, page.updated_at or page.created_at)}</strong></div>
        </div>
    </div>
</header>