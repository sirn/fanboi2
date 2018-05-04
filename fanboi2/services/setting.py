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
        will automatically expire cache for the given key if exists.

        :param key: The setting key.
        :param value: The value to set.
        """
        stmt = insert(Setting.__table__)
        stmt = stmt.\
            values(key=key, value=value).\
            returning(Setting.key).\
            on_conflict_do_update(
                index_elements=[Setting.key],
                set_=dict(value=stmt.excluded.value))
        result = self.dbsession.execute(stmt)
        key_ = result.fetchone()[0]
        cache_key = _get_cache_key(key)
        self.cache_region.delete(cache_key)
        result.close()
        return self.dbsession.query(Setting).filter_by(key=key_).first()
