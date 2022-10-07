<%include file="_subheader.mako" />
<%inherit file="../partials/_layout.mako" />
<%def name="title()">${topic.title} - ${board.title}</%def>
<%def name="header()"><meta http-equiv="refresh" content="3; url=${request.path_qs}"></%def>
<div class="panel">
    <div class="container u-pd-vertical-xl">
        <h2 class="panel__item u-mg-bottom-xs u-txt-brand">Processing post...</h2>
        <p class="panel__item u-mg-bottom-xs">Your post is currently processing. You will be redirected automatically.</p>
        <p class="panel__item u-mg-bottom-m">If you are not getting redirected after few seconds, please click retry below.</p>
        <div class="panel__item">
            <a class="btn btn--shadowed btn--gray4" href="${request.path_qs}">Retry</a>
        </div>
    </div>
</div>
