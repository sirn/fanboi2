<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%def name="render_datetime(datetime)">
    <time datetime="${formatters.format_isotime(request, datetime)}">${formatters.format_datetime(request, datetime)}</time>
</%def>