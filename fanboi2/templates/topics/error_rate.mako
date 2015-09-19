<%namespace name="posts_" file="../partials/_posts.mako" />
<%inherit file="../partials/_layout.mako" />
<%include file="_header.mako" />
<%def name="title()">${topic.title} - ${board.title}</%def>
<div class="item-error">
    <div class="container">
        <h2 class="title">You are posting too fast.</h2>
        <p class="description">Please wait <strong>${timeleft} seconds</strong> before retrying.</p>
    </div>
</div>
