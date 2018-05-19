<%inherit file='../partials/_layout.mako' />
<%def name='header()'><link rel="stylesheet" href="${request.tagged_static_path('fanboi2:static/admin.css')}"></%def>
% if hasattr(self, 'subheader_title') and hasattr(self, 'subheader_body'):
<header class="subheader">
    <div class="container">
        <h2 class="subheader-title">${self.subheader_title()}</h2>
        <div class="subheader-body"><p>${self.subheader_body()}</p></div>
    </div>
</header>
% endif
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
                        </ul>
                        <h3 class="menu-header">System</h3>
                        <ul class="menu-actions">
                            <li class="menu-actions-item"><a href="${request.route_path('admin_pages')}">Pages</a></li>
                            <li class="menu-actions-item"><a href="${request.route_path('admin_settings')}">Settings</a></li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="cols-column">
                ${next.body()}
            </div>
        </div>
    </div>
</div>