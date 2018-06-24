<%include file='_subheader.mako' />
<%inherit file='../partials/_layout.mako' />
<%def name='title()'>New topic - ${board.title}</%def>
<div class="sheet">
    <div class="container">
    % if name == 'akismet_rejected':
        <h2 class="sheet-title">I'm sorry, Dave. I'm afraid I can't do that.</h2>
        <div class="sheet-body">
            <p>This mission is too important for me to allow you to jeopardize it.</p>
            <p><em>Your topic has been identified as spam by Akismet and therefore rejected.</em></p>
        </div>
    % elif name == 'ban_rejected':
        <h2 class="sheet-title">You cannot pass.</h2>
        <div class="sheet-body">
            <p>The dark fire will not avail you. Go back to the Shadow!</p>
            <p><em>Your IP address is being listed in the ban list.</em></p>
        </div>
    % elif name == 'banword_rejected':
        <h2 class="sheet-title">It's a beautiful thing, the destruction of words.</h2>
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
    % endif
    </div>
</div>
