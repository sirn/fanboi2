from ..models.setting import DEFAULT_SETTINGS, Setting


class SettingQueryService(object):
    """Setting query service provides a service for querying a runtime
    application settings that are not part of startup process, such as
    timezone.
    """

    def __init__(self, dbsession, cache_region):
        self.dbsession = dbsession
        self.cache_region = cache_region

    def _get_cache_key(self, key):
        """Returns a cache key for given key.

        :param key: The setting key.
        """
        return 'services.settings:key=%s' % (key,)

    def value_from_key(self, key, _default=DEFAULT_SETTINGS):
        """Returns a setting value either from a cache, from a database
        or the default value. The value returned by this method will be
        cached for 3600 seconds (1 hour).

        :param key: The setting key.
        """
        def _creator_fn():
            setting = self.dbsession.query(Setting).filter_by(key=key).first()
            if not setting:
                return _default.get(key, None)
            return setting.value
        return self.cache_region.get_or_create(
            self._get_cache_key(key),
            _creator_fn,
            expiration_time=3600)

    def reload(self, key):
        """Delete the given key from the cache to force reloading
        of the settings the next time it is accessed.

        :param key: The setting key.
        """
        cache_key = self._get_cache_key(key)
        return self.cache_region.delete(cache_key)
