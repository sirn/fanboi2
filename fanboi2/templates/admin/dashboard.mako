<%inherit file='../partials/_layout.mako' />
<%def name='title()'>Login - Admin Panel</%def>
<header class="subheader">
    <div class="container">
        <h2 class="subheader-title">Dashboard</h2>
        <div class="subheader-body"><p>Overview of the site.</p></div>
    </div>
</header>
<div class="sheet">
    <div class="container">
        <div class="cols">
            <div class="cols-column sidebar">
                <div class="sheet-body">
                    <div class="menu">
                        <h3 class="menu-header">My Actions</h3>
                        <ul class="menu-actions">
                            <li class="menu-actions-item"><a href="${request.route_path('admin_dashboard')}">Dashboard</a></li>
                            <li class="menu-actions-item"><a href="${request.route_path('admin_logout')}">Logout</a></li>
                        </ul>
                        <h3 class="menu-header">Moderation</h3>
                        <ul class="menu-actions">
                            <li class="menu-actions-item"><a href="${request.route_path('admin_bans')}">Bans</a></li>
                            <li class="menu-actions-item"><a href="${request.route_path('admin_boards')}">Boards</a></li>
                            <li class="menu-actions-item"><a href="${request.route_path('admin_topics')}">Topics</a></li>
                        </ul>
                        <h3 class="menu-header">System</h3>
                        <ul class="menu-actions">
                            <li class="menu-actions-item"><a href="${request.route_path('admin_pages')}">Pages</a></li>
                            <li class="menu-actions-item"><a href="${request.route_path('admin_settings')}">Settings</a></li>
                            <li class="menu-actions-item"><a href="${request.route_path('admin_users')}">Users</a></li>
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