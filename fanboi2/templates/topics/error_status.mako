<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>${topic.title} - ${board.title}</%def>
<div class="sheet">
    <div class="container">
        % if status == 'locked':
            <h2 class="sheet-title">Don't panic.</h2>
            <div class="sheet-body">
                <p>There's no point in acting surprised about it.</p>
                % if topic.status == 'locked':
                    <p><em>Topic has been locked by moderator due to requests.</em></p>
                % else
                    <p><em>Board has been locked by moderator.</em></p>
                % endif
            </div>
        % elif status == 'archived':
            <h2 class="sheet-title">A candle that burns twice as bright, burns half as long.</h2>
            <div class="sheet-body">
                <p>Nothing the god of biomechanics wouldn't let you in heaven for.</p>
                % if topic.status == 'locked':
                    <p><em>Topic has reached maximum number of posts.</em></p>
                % else
                    <p><em>Board has been archived.</em></p>
                % endif
            </div>
        % endif
    </div>
</div>
