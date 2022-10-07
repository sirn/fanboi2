<%namespace name="ident" file="../../../partials/_ident.mako" />
<%namespace name="nav" file="_nav.mako"/>
<%inherit file="../../_layout.mako" />
<%def name="title()">${board.title} - Admin Panel</%def>
<%nav:render_nav title="${board.title}" board="${board}" />
<div class="sheet-body">
    <form class="form" action="${request.route_path('admin_board_topic_new', board=board.slug)}" method="post">
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
            <p>Posting as <strong>${user.name}</strong> with ident <strong>${ident.render_ident(user.ident, user.ident_type)}</strong></p>
            % if board.status == 'restricted':
                <p>Board is currently <strong>restricted</strong>. You can create a new topic and user will be able to respond.</p>
            % elif board.status == 'locked':
                <p>Board is currently <strong>locked</strong>. You can create a new topic, but other users won't be able to respond.</p>
            % endif
        </div>
        <div class="form-item">
            <button class="btn btn--shadowed btn--primary" type="submit">Create Topic</button>
        </div>
    </form>
</div>
