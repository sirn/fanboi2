<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="partials" module="fanboi2.helpers.partials" />
<%namespace name="info" module="fanboi2.helpers.info" />
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1">
    <meta name="theme-color" content="#fc2e05">

    <link rel="icon" href="${request.tagged_static_path('fanboi2:static/icon.png')}" sizes="256x256">
    <link rel="shortcut icon" href="${request.tagged_static_path('fanboi2:static/icon.ico')}" type="image/x-icon">
    <link rel="apple-touch-icon" href="${request.tagged_static_path('fanboi2:static/touch-icon.png')}">
    <link rel="stylesheet" href="${request.tagged_static_path('fanboi2:static/app.css')}">
    <title>${self.title() + ' - ' if hasattr(self, 'title') else ''}Fanboi Channel</title>
    % if hasattr(self, 'header'):
        ${self.header()}
    % endif

    <% global_css = partials.global_css(request) %>
    % if global_css:
        <style>
            ${global_css}
        </style>
    % endif
</head>
% if hasattr(self, 'body_args'):
<body id="${request.route_name}" class="${formatters.user_theme(request)}" ${self.body_args()}>
% else:
<body id="${request.route_name}" class="${formatters.user_theme(request)}">
% endif

<header id="top" class="header" data-board-selector="true">
    <div class="container">
        <h1 class="header-brand"><a href="/">Fanboi Channel</a></h1>
        <div class="header-scroll-button"><a href="#bottom">Scroll to bottom</a></div>
    </div>
</header>

${next.body()}

<section class="appendix">
    <div class="container">
<% global_appendix = partials.global_appendix(request) %>
% if global_appendix:
        <div class="appendix-content">
            ${global_appendix}
        </div>
% endif
        <div class="appendix-lines" data-theme-selector="true">
            <p class="appendix-lines-item">All contents are responsibility of its posters.</p>
        </div>
    </div>
</section>

<footer id="bottom" class="footer">
    <div class="container">
        <div class="footer-scroll-button">
          <a href="#top">Scroll to top</a>
        </div>
        <ul class="footer-links">
            <li class="footer-links-item"><a href="https://git.sr.ht/~sirn/fanboi2">Fanboi2 v${info.app_version(request)}</a></li>
            <li class="footer-links-item"><a href="${request.route_path('api_root')}">API documentation</a></li>
        </ul>
    </div>
</footer>

<script type="text/javascript" src="${request.tagged_static_path('fanboi2:static/main.bundle.js')}"></script>
<script type="text/javascript" src="${request.tagged_static_path('fanboi2:static/runtime.bundle.js')}"></script>

<% global_footer = partials.global_footer(request) %>
% if global_footer:
    ${global_footer}
% endif
</body>
</html>
