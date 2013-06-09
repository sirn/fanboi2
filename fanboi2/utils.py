import requests


class Akismet(object):
    def __init__(self, request):
        self.key = request.registry.settings.get('akismet.api')

    def ham(self, message):
        return False
