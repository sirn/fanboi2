from redis import StrictRedis


def includeme(config):  # pragma: no cache
    redis_url = config.registry.settings['redis.url']
    redis_conn = StrictRedis.from_url(redis_url)

    def redis_conn_factory(context, request):
        return redis_conn

    config.register_service_factory(redis_conn_factory, name='redis')
