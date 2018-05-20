<%namespace name="datetime" file="../partials/_datetime.mako" />
<header class="subheader">
    <div class="container">
        <h2 class="subheader-title"><a href="${request.route_path('page', page=page.slug)}">${page.title}</a></h2>
        <div class="subheader-body lines">Updated <strong>${datetime.render_datetime(page.updated_at or page.created_at)}</strong></div>
    </div>
</header>