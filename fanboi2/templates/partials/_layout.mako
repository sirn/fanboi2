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

    <link rel="stylesheet" href="${request.tagged_static_path('fanboi2:static/vendor.css')}">
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

<header id="top" class="panel panel--brand" data-board-selector="true">
    <div class="container">
        <div class="header header--h-container">
            <div class="header__item header__item--logo"><h1 class="u-mg-reset"><a href="/" class="icon header__icon-logo">Fanboi Channel</a></h1></div>
            <div class="header__item header__item--board"><a href="/" class="icon icon--tappable icon--burger-white" data-board-selector-button="true">All boards</a></div>
            <div class="header__item header__item--scroll"><a href="#bottom" class="icon icon--tappable icon--arrow-down-white">Scroll to bottom</a></div>
        </div>
    </div>
</header>

${next.body()}

<section class="panel panel--shade4">
    <div class="container u-pd-vertical-l">
<% global_appendix = partials.global_appendix(request) %>
% if global_appendix:
        <div class="panel__item u-mg-bottom-m u-txt-plain u-txt-s u-txt-gray4">
            ${global_appendix}
        </div>
% endif
        <div class="panel__item u-txt-gray4" data-theme-selector="true">
            <p class="u-mg-reset u-txt-s">All contents are responsibility of its posters.</p>
        </div>
    </div>
</section>

<footer id="bottom" class="panel">
    <div class="container u-pd-vertical-l">
        <div class="panel__item">
            <a href="#top" class="icon icon--tappable icon--arrow-up-blue u-pull-right">Scroll to top</a>
            <ul class="list flex--column">
                <li class="list__item flex__item u-txt-s"><a href="https://git.sr.ht/~sirn/fanboi2">Fanboi2 v${info.app_version(request)}</a></li>
                <li class="list__item flex__item u-txt-s"><a href="${request.route_path('api_root')}">API documentation</a></li>
            </ul>
        </div>
    </div>
</footer>

<script type="text/javascript" src="${request.tagged_static_path('fanboi2:static/vendor.js')}"></script>
<script type="text/javascript" src="${request.tagged_static_path('fanboi2:static/app.js')}"></script>

<% global_footer = partials.global_footer(request) %>
% if global_footer:
    ${global_footer}
% endif

</body>
</html>
