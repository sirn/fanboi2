<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>${topic.title} - ${board.title}</%def>
<%def name='header()'><meta http-equiv="refresh" content="3; url=${request.path_qs}"></%def>
<div class="sheet">
    <div class="container">
        <h2 class="sheet-title">Processing post...</h2>
        <div class="sheet-body">
            <p>Your post is currently processing. You will be redirected automatically.</p>
            <p>If you're not getting redirected after few seconds, please click retry below.</p>
        </div>
        <div class="sheet-body">
            <a class="button muted" href="${request.path_qs}">Retry</a>
        </div>
    </div>
</div>
