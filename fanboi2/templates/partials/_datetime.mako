<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%def name="render_datetime(datetime)">
% if datetime is not None:
    <time datetime="${formatters.format_isotime(request, datetime)}">${formatters.format_datetime(request, datetime)}</time>
% endif
</%def>
