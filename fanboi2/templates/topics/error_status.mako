<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>${topic.title} - ${board.title}</%def>
<div class="sheet">
    <div class="container">
        % if status == 'locked':
            <h2 class="sheet-title">Don't panic.</h2>
            <div class="sheet-body">
                <p>There's no point in acting surprised about it.</p>
                <p><em>Topic has been locked by moderator due to requests.</em></p>
            </div>
        % elif status == 'archived':
            <h2 class="sheet-title">A candle that burns twice as bright, burns half as long.</h2>
            <div class="sheet-body">
                <p>Nothing the god of biomechanics wouldn't let you in heaven for.</p>
                <p><em>Topic has reached maximum number of posts.</em></p>
            </div>
        % endif
    </div>
</div>
