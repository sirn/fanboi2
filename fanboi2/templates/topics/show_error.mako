<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>${topic.title} - ${board.title}</%def>
<div class="sheet">
    <div class="container">
    % if name == 'akismet_rejected':
        <h2 class="sheet-title">I'm sorry, Dave. I'm afraid I can't do that.</h2>
        <div class="sheet-body">
            <p>This mission is too important for me to allow you to jeopardize it.</p>
            <p><em>Your post has been identified as spam and therefore rejected.</em></p>
        </div>
    % elif name == 'ban_rejected':
        <h2 class="sheet-title">You cannot pass.</h2>
        <div class="sheet-body">
            <p>The dark fire will not avail you. Go back to the Shadow!</p>
            <p><em>Your IP address is being listed in the ban list.</em></p>
        </div>
    % elif name == 'banword_rejected':
        <h2 class="sheet-title">It's a beautiful thing, the Destruction of words.</h2>
        <div class="sheet-body">
            <p>There are hundreds of nouns that can be got rid of as well</p>
            <p><em>Your post contained a forbidden keyword and therefore rejected.</em></p>
        </div>
    % elif name == 'dnsbl_rejected':
        <h2 class="sheet-title">A strange game.</h2>
        <div class="sheet-body">
            <p>The only winning move is not to play. How about a nice game of chess?</p>
            <p><em>Your IP address is listed in DNSBL and therefore rejected.</em></p>
        </div>
    % elif name == 'proxy_rejected':
        <h2 class="sheet-title">You look surprised to see me, again, Mr. Anderson.</h2>
        <div class="sheet-body">
            <p>That's the difference between us. I've been expecting you.</p>
            <p><em>Your IP address has been identified as an open proxy or public VPN.</em></p>
        </div>
    % elif name == 'rate_limited':
        <h2 class="sheet-title">Nothing travels faster than light.</h2>
        <div class="sheet-body">
            <p>With the possible exception of bad news, which obeys its own special laws.</p>
            <p><em>You're posting too fast. Please wait <strong>${time_left} seconds</strong> before trying again.</em></p>
        </div>
    % elif name == 'status_rejected':
        % if status == 'locked':
            <h2 class="sheet-title">Don't panic.</h2>
            <div class="sheet-body">
                <p>There's no point in acting surprised about it.</p>
                % if topic.status == 'locked':
                    <p><em>Topic has been locked by moderator due to requests.</em></p>
                % else:
                    <p><em>Board has been locked by moderator.</em></p>
                % endif
            </div>
        % elif status == 'archived':
            <h2 class="sheet-title">A candle that burns twice as bright, burns half as long.</h2>
            <div class="sheet-body">
                <p>Nothing the god of biomechanics wouldn't let you in heaven for.</p>
                % if topic.status == 'locked':
                    <p><em>Topic has reached maximum number of posts.</em></p>
                % else:
                    <p><em>Board has been archived.</em></p>
                % endif
            </div>
        % endif
    % endif
    </div>
</div>
