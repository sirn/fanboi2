<%inherit file='../partials/_layout.mako' />
<%def name='title()'>Login - Admin Panel</%def>
<header class="subheader">
    <div class="container">
        <h2 class="subheader-title">Admin Panel</h2>
        <div class="subheader-body"><p>Manage various aspect of the site.</p></div>
    </div>
</header>
<div class="sheet">
    <div class="container">
        <h2 class="sheet-title">Dashboard</h2>
        <div class="cols">
            <div class="cols-column sidebar">
                <div class="sheet-body">
                    <div class="menu">
                        <h3 class="menu-header">My</h3>
                        <ul class="menu-actions">
                            <li class="menu-actions-item"><a href="/">Dashboard</a></li>
                            <li class="menu-actions-item"><a href="/">Logout</a></li>
                        </ul>
                        <h3 class="menu-header">Moderation</h3>
                        <ul class="menu-actions">
                            <li class="menu-actions-item"><a href="/">Bans</a></li>
                            <li class="menu-actions-item"><a href="/">Boards</a></li>
                            <li class="menu-actions-item"><a href="/">Topics</a></li>
                        </ul>
                        <h3 class="menu-header">System</h3>
                        <ul class="menu-actions">
                            <li class="menu-actions-item"><a href="/">Pages</a></li>
                            <li class="menu-actions-item"><a href="/">Settings</a></li>
                            <li class="menu-actions-item"><a href="/">Users</a></li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="sheet-body">
                body
            </div>
        </div>
    </div>
</div>