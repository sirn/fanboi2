<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="partials" module="fanboi2.helpers.partials" />
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1">

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
    <body id="${request.route_name}" class="${formatters.user_theme(request)}">

        <header id="top" class="panel panel--inverse ${self.header_class() + ' ' if hasattr(self, 'header_class') else ''}header" data-board-selector="true">
            <div class="container header__container">
                <a class="header__logo" href="/">Fanboi Channel</a>
                <a class="header__button icon icon--burger util-pull-left" href="/">Sidebar</a>
                <a class="header__button icon icon--arrow util-pull-right" href="#bottom">Scroll to bottom</a>
            </div>
        </header>

        ${next.body()}

        <% global_appendix = partials.global_appendix(request) %>
        % if global_appendix:
            <div class="panel panel--inverse util-backdrop">
                <div class="container">
                    <div class="panel__item util-padded util-text-small typo-plain">
                        ${global_appendix}
                    </div>
                </div>
            </div>
        % endif

        <footer class="panel util-text-small footer" id="bottom">
            <div class="container footer__container">
                <div class="util-padded">
                    All contents are reponsibility of its poster.
                    <ul class="footer__right links">
                        <li class="links__item"><a href="${request.route_path('api_root')}">API documentation</a></li>
                        <li class="links__item"><a href="https://git.sr.ht/~sirn/fanboi2">Source code</a></li>
                    </ul>
                </div>
                <a class="footer__up icon icon--arrow-up" href="#top">Scroll to top</a>
            </div>
        </footer>

        <script type="text/javascript" src="${request.tagged_static_path('fanboi2:static/app.js')}"></script>

        <% global_footer = partials.global_footer(request) %>
        % if global_footer:
            ${global_footer}
        % endif

    </body>
</html>
