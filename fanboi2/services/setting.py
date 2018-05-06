import json

from sqlalchemy.dialects.postgresql import insert

from ..models.setting import DEFAULT_SETTINGS, Setting


def _get_cache_key(key):
    """Returns a cache key for given key.

    :param key: The setting key.
    """
    return 'services.settings:key=%s' % (key,)


class SettingQueryService(object):
    """Setting query service provides a service for querying a runtime
    application settings that are not part of startup process, such as
    timezone.
    """

    def __init__(self, dbsession, cache_region):
        self.dbsession = dbsession
        self.cache_region = cache_region

    def _jsonify(self, value):
        return json.dumps(value, indent=4, sort_keys=True)

    def list_json(self, _default=DEFAULT_SETTINGS):
        """Returns a 2-tuple of all settings where its values are JSONified.
        This method will only return the safe settings that are explicitly
        defined within the list of default settings.
        """
        all_settings = []
        for key in sorted(_default.keys()):
            all_settings.append((
                key,
                self._jsonify(self.value_from_key(key, _default=_default))))
        return all_settings

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
            _get_cache_key(key),
            _creator_fn,
            expiration_time=3600)

    def value_from_key_json(self, key, _default=DEFAULT_SETTINGS):
        """Similar to :meth:`value_from_key` but returns a JSONified value.
        This method should be used when displaying the settings data and will
        raise ``KeyError`` if the given key is not considered safe.

        :param key: The setting key.
        """
        if key not in _default:
            raise KeyError(key)
        value = self.value_from_key(key, _default=_default)
        return self._jsonify(value)

    def reload(self, key):
        """Delete the given key from the cache to force reloading
        of the settings the next time it is accessed.

        :param key: The setting key.
        """
        cache_key = _get_cache_key(key)
        return self.cache_region.delete(cache_key)


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
        will automatically reload cache for the given key.

        :param key: The setting key.
        :param value: The value to set.
        """
        setting = self.dbsession.query(Setting).filter_by(key=key).first()
        if setting is None:
            setting = Setting(key=key)
        setting.value = value
        self.dbsession.add(setting)
        self.cache_region.set(_get_cache_key(key), value)
        return setting
