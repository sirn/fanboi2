<%inherit file="../partials/_layout.mako" />
<%include file="_header.mako" />
<%def name="title()">${board.title}</%def>
<%def name="header()"><meta http-equiv="refresh" content="1; url=${request.path_qs}"></%def>
<div class="item-error">
    <div class="container">
        <h2 class="title">Please wait.</h2>
        <p class="description">Your post is now processing. You will be redirected automatically.</p>
    </div>
</div>
