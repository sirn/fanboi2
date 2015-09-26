<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>${topic.title} - ${board.title}</%def>
<div class="sheet">
    <div class="container">
        <h2 class="sheet-title">Nothing travels faster than light.</h2>
        <div class="sheet-body">
            <p>With the possible exception of bad news, which obeys its own special laws.</p>
            <p><em>You're posting too fast. Please wait <strong>${timeleft} seconds</strong> before trying again.</em></p>
        </div>
    </div>
</div>
