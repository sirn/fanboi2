<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<%inherit file='../../_layout.mako' />
<%def name='title()'>${board.title} - Admin Panel</%def>
<%def name='subheader_title()'>Topics</%def>
<%def name='subheader_body()'>Manage topics.</%def>
<h2 class="sheet-title">${board.title}</h2>
<%include file='_nav.mako' />
<form class="form noshade" action="${request.route_path('admin_board_topic_new', board=board.slug)}" method="post">
    <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
    <div class="form-item${' error' if form.title.errors else ''}">
        <label class="form-item-label" for="${form.title.id}">Title</label>
        ${form.title(class_="input block font-large")}
        % if form.title.errors:
            <span class="form-item-error">${form.title.errors[0]}</span>
        % endif
    </div>
    <div class="form-item${' error' if form.body.errors else ''}">
        <label class="form-item-label" for="${form.body.id}">Body</label>
        ${form.body(class_="input block font-large", rows=6)}
        % if form.body.errors:
            <span class="form-item-error">${form.body.errors[0]}</span>
        % endif
    </div>
    <div class="form-item">
        <p>Posting as <strong>${user.name}</strong> with ident <strong>${user.ident}</strong></p>
        % if board.status == 'restricted':
        <p>Board is currently <strong>restricted</strong>. You can create a new topic and user will be able to respond.</p>
        % elif board.status == 'locked':
        <p>Board is currently <strong>locked</strong>. You can create a new topic, but other users won't be able to respond.</p>
        % endif
    </div>
    <div class="form-item">
        <button class="button green" type="submit">Create Topic</button>
    </div>
</form>