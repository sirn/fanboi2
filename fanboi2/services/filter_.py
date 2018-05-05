from collections import namedtuple

from ..interfaces import ISettingQueryService, IPostQueryService


FilterResult = namedtuple('FilterResult', ('rejected_by', 'filters'))


class FilterService(object):
    """Filter service provides a service for evaluating content using
    predefined sets of pre-posting filters.
    """

    def __init__(self, filters, service_query_fn):
        self.filters = filters
        self.service_query_fn = service_query_fn

    def evaluate(self, payload):
        """Evaluate the given payload with filters.

        :param payload: A filter payload to verify.
        """
        filters_chain = []
        setting_query_svc = self.service_query_fn(ISettingQueryService)

        if 'ip_address' in payload:
            post_query_svc = self.service_query_fn(IPostQueryService)
            if post_query_svc.was_recently_seen(payload['ip_address']):
                return FilterResult(rejected_by=None, filters=[])

        for name, cls in self.filters:
            services = {}
            filters_chain.append(name)
            if hasattr(cls, '__use_services__'):
                for s in cls.__use_services__:
                    services[s] = self.service_query_fn(name=s)

            settings_name = "ext.filters.%s" % (name,)
            settings = setting_query_svc.value_from_key(settings_name)

            f = cls(settings, services)
            if f.should_reject(payload):
                return FilterResult(rejected_by=name, filters=filters_chain)

        return FilterResult(rejected_by=None, filters=filters_chain)
