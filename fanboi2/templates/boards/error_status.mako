<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>New topic - ${board.title}</%def>
<div class="sheet">
    <div class="container">
    % if status == 'restricted':
        <h2 class="sheet-title">Is that your two cents worth, Worth?</h2>
        <div class="sheet-body">
            <p>For what it’s worth…</p>
            <p><em>Board is currently disallow creation of new topic.</em></p>
        </div>
    % elif status == 'locked':
        <h2 class="sheet-title">Too much garbage in your face?</h2>
        <div class="sheet-body">
            <p>There's plenty of space out in space!</p>
            <p><em>Board has been locked by moderator.</em></p>
        </div>
    % elif status == 'archived':
        <h2 class="sheet-title">Hasta la vista, baby.</h2>
        <div class="sheet-body">
            <p>You gotta listen to the way people talk.</p>
            <p><em>Board has been archived.</em></p>
        </div>
    % endif
    </div>
</div>