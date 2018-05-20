<%def name="render_ident(ident, ident_type='ident', class_=None)">
    % if ident:
    <span class="${class_ + ' ' if class_ else ''}ident${' ' + ident_type.replace('_', '-') if ident_type != 'ident' else ''}">ID:${ident}</span>
    % endif
</%def>