from ..models.setting import DEFAULT_SETTINGS, Setting


def _get_cache_key(key):
    """Returns a cache key for given key.

    :param key: The setting key.
    """
    return "services.setting:key=%s" % (key,)


class SettingQueryService(object):
    """Setting query service provides a service for querying a runtime
    application settings that are not part of startup process, such as
    timezone.
    """

    def __init__(self, dbsession, cache_region):
        self.dbsession = dbsession
        self.cache_region = cache_region

    def list_all(self, _default=DEFAULT_SETTINGS):
        """Returns a 2-tuple of all settings. This method only return
        the safe settings that are explicitly defined.
        """
        db_settings = self.dbsession.query(Setting).all()
        seen_keys = []
        safe_keys = _default.keys()
        safe_settings = []
        for setting in db_settings:
            if setting.key in safe_keys:
                safe_settings.append((setting.key, setting.value))
                seen_keys.append(setting.key)
        for key in safe_keys:
            if key not in seen_keys:
                safe_settings.append((key, _default.get(key, None)))
        return sorted(safe_settings)

    def value_from_key(
        self, key, use_cache=True, safe_keys=False, _default=DEFAULT_SETTINGS
    ):
        """Returns a setting value either from a cache, from a database
        or the default value. The value returned by this method will be
        cached for 3600 seconds (1 hour).

        :param key: The :type:`str` setting key.
        :param use_cache: A :type:`bool` flag whether to load from cache.
        """

        def _creator_fn():
            setting = self.dbsession.query(Setting).filter_by(key=key).first()
            if not setting:
                return _default.get(key, None)
            return setting.value

        if safe_keys and key not in _default:
            raise KeyError(key)
        if use_cache:
            return self.cache_region.get_or_create(
                _get_cache_key(key), _creator_fn, expiration_time=3600
            )
        return _creator_fn()

    def reload_cache(self, key):
        """Replace the given key from the cache to force reloading
        of the settings the next time it is accessed.

        :param key: The setting key.
        """
        return self.cache_region.delete(_get_cache_key(key))


class SettingUpdateService(object):
    """Setting update service provides a service for updating a runtime
    application settings that are not part of startup process.
    """

    def __init__(self, dbsession, cache_region):
        self.dbsession = dbsession
        self.cache_region = cache_region

    def update(self, key, value):
        """Update the given setting key with the given value. The value
        may be any data structure that are JSON-serializable. This method
        will automatically invalidate cache for the given key.

        :param key: The setting key.
        :param value: The value to set.
        """
        setting = self.dbsession.query(Setting).filter_by(key=key).first()
        if setting is None:
            setting = Setting(key=key)
        setting.value = value
        self.dbsession.add(setting)
        self.cache_region.delete(_get_cache_key(key))
        return setting
