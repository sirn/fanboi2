<%namespace name="datetime" file="../partials/_datetime.mako" />
<header class="panel panel--inverse util-padded-bottom">
    <div class="container">
        <h2 class="panel__item"><a class="util-text-gray" href="${request.route_path('page', page=page.slug)}">${page.title}</a></h2>
        <div class="panel__item util-text-gray">Updated ${datetime.render_datetime(page.updated_at or page.created_at)}</div>
    </div>
</header>
