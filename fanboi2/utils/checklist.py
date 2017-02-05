class Checklist(object):
    """Utility for evaluating checklist."""

    def __init__(self):
        self.data = {}

    def configure_checklist(self, config):
        """Configure the checklist with the given ``config``.

        :param config: List of strings containing checklist configuration.
        :type config: str[]
        """
        if config:
            for data in config:
                scope, items = data.split('/', 1)
                self.data[scope] = [r for r in items.split(',') if r]

    def fetch(self, scope):
        """Fetch the enabled rules according to the given scope. This method
        will return ``['*']`` if no rules was defined for the given scope.
        In which the application should treat such rule as enable all.

        :param scope: Name of the scope to use for lookup.
        :type scope: str
        :rtype: str[]
        """
        data = self.data.get(scope, None)
        if data is None:
            data = self.data.get('*', ['*'])
        return data

    def enabled(self, scope, target):
        """Check if the given ``target`` was enabled in the given ``scope``.

        :param scope: Name of the scope to use for lookup.
        :param target: Name of the target rule to check against.
        :type scope: str
        :type target: str
        :rtype: bool
        """
        items = self.fetch(scope)
        return target in items or '*' in items
