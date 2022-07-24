<%inherit file='../../_layout.mako' />
<%def name='title()'>${board.title} - Admin Panel</%def>
<%def name='subheader_title()'>Topics</%def>
<%def name='subheader_body()'>Manage topics.</%def>
<h2 class="sheet-title">${topic.title}</h2>
<%include file='_nav.mako' />
<div class="sheet-body">
    <form class="form" action="${request.route_path('admin_board_topic_edit', board=board.slug, topic=topic.id)}" method="post">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="form-item${' error' if form.status.errors else ''}">
            <label class="form-item-label" for="${form.status.id}">Status</label>
            ${form.status()}
            % if form.status.errors:
                <span class="form-item-error">${form.status.errors[0]}</span>
            % endif
        </div>
        <div class="form-item">
            <button class="button brand" type="submit">Update Topic</button>
        </div>
    </form>
</div>
