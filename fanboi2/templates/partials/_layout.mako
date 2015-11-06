<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1">

    <link rel="icon" href="${request.tagged_static_path('fanboi2:static/icon.png')}" sizes="256x256">
    <link rel="shortcut icon" href="${request.tagged_static_path('fanboi2:static/icon.ico')}" type="image/x-icon">
    <link rel="apple-touch-icon" href="${request.tagged_static_path('fanboi2:static/touch-icon.png')}">

    <link rel="stylesheet" href="${request.tagged_static_path('fanboi2:static/vendor.css')}">
    <link rel="stylesheet" href="${request.tagged_static_path('fanboi2:static/app.css')}">
    <!--[if IE]><script type="text/javascript" src="${request.tagged_static_path('fanboi2:static/legacy.js')}"></script><![endif]-->

    <title>${self.title() + ' - ' if hasattr(self, 'title') else ''}Fanboi Channel</title>

    % if hasattr(self, 'header'):
        ${self.header()}
    % endif
</head>
<body id="${request.route_name}" class="theme-topaz">

<header class="header">
    <div class="container">
        <h1 class="header-brand"><a href="/">Fanboi Channel</a></h1>
    </div>
</header>

${self.body()}

<footer class="footer">
    <div class="container">
        <div class="footer-lines">
            <p class="footer-lines-item">All contents are responsibility of its posters.</p>
            <p class="footer-lines-item">Fanboi2 is an <a href="https://github.com/pxfs/fanboi2">open-source</a> project.</p>
        </div>
        <ul class="footer-links">
            <li class="footer-links-item"><a href="${request.route_path('api_root')}">API documentation</a></li>
            <li class="footer-links-item"><a href="https://twitter.com/fanboich">Twitter</a></li>
        </ul>
    </div>
</footer>

<script type="text/javascript" src="${request.tagged_static_path('fanboi2:static/vendor.js')}"></script>
<script type="text/javascript" src="${request.tagged_static_path('fanboi2:static/app.js')}"></script>

</body>
</html>
