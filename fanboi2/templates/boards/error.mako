<%inherit file="../partials/_layout.mako" />
<%include file="_header.mako" />
<%def name="title()">${board.title}</%def>
<div class="item-error">
    <div class="container">
        <h2 class="title">You are posting too fast.</h2>
        <p class="description">Please wait <strong>${ratelimit.timeleft()} seconds</strong> before retrying.</p>
    </div>
</div>
