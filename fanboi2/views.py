from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='index')
def index_view(request):
    return Response("Hello, world!")
