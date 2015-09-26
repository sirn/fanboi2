<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>${topic.title} - ${board.title}</%def>
<div class="sheet">
    <div class="container">
        <h2 class="sheet-title">I'm sorry, Dave. I'm afraid I can't do that.</h2>
        <div class="sheet-body">
            <p>This mission is too important for me to allow you to jeopardize it.</p>
            <p><em>Your post has been identified as spam and therefore rejected.</em></p>
        </div>
    </div>
</div>
