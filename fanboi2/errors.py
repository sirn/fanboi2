class BaseError(Exception):
    """A base :class:`Exception` class that provides hint for reporting
    errors as JSON response.
    """

    def message(self, request):
        """A serializable object to be include in the response as error
        message. The return type of this method is not necessary a string,
        it may be a list of string, a dict containing string or some other
        serializable types.

        :param request: A :class:`pyramid.request.Request` object.
        """
        return 'An exception error occurred.'

    @property
    def name(self):
        """The short globally recognizable name of this error."""
        return 'unknown'

    @property
    def http_status(self):
        """The HTTP status code to response as."""
        return '500 Internal Server Error'


class RateLimitedError(BaseError):
    """An :class:`Exception` class that will be raised if user request was
    blocked due to rate limiter. The time left until user is unblocked could
    be accessed from :property:`timeleft`.

    :param timeleft: An :type:`int` in seconds until user is unblocked.
    """

    def __init__(self, timeleft):
        self.timeleft = timeleft

    def message(self, request):
        return 'Please wait %s seconds before retrying.' % self.timeleft

    @property
    def name(self):
        return 'rate_limited'

    @property
    def http_status(self):
        return '429 Too Many Requests'


class ParamsInvalidError(BaseError):
    """An :class:`Exception` class that will be raised if user request could
    not be processed due to form being invalid. Error messages are stored
    inside :property:`messages`.

    :param messages: An :type:`dict` of :type:`list` of field errors.
    """

    def __init__(self, messages):
        self.messages = messages

    def message(self, request):
        return self.messages

    @property
    def name(self):
        return 'params_invalid'

    @property
    def http_status(self):
        return '400 Bad Request'


class AkismetRejectedError(BaseError):
    """An :class:`Exception` class that will be raised if user request was
    blocked due user request failed a spam check.
    """

    def message(self, request):
        return 'The request has been identified as spam ' +\
            'by Akismet and therefore rejected.'

    @property
    def name(self):
        return 'akismet_rejected'

    @property
    def http_status(self):
        return '422 Unprocessable Entity'


class DNSBLRejectedError(BaseError):
    """An :class:`Exception` class that will be raised if user request was
    blocked due user IP address failed an DNSBL check.
    """

    def message(self, request):
        return 'The IP address is being listed in one of DNSBL databases ' +\
            'and therefore rejected.'

    @property
    def name(self):
        return 'dnsbl_rejected'

    @property
    def http_status(self):
        return '422 Unprocessable Entity'


class BanRejectedError(BaseError):
    """An :class:`Exception` class that will be raised if user request was
    blocked due user IP address being listed in the ban list.
    """

    def message(self, request):
        return 'The IP address is being listed in the ban list ' +\
            'and therefore rejected.'

    @property
    def name(self):
        return 'ban_rejected'

    @property
    def http_status(self):
        return '422 Unprocessable Entity'


class StatusRejectedError(BaseError):
    """An :class:`Exception` class that will be raised if user request was
    blocked due the topic or the board being locked. The status that caused
    the lock could be retrieved from :property:`status`.

    :param status: A :type:`str` of the status that caused the block.
    """

    def __init__(self, status):
        self.status = status

    def message(self, request):
        return 'The topic or the board is currently locked.'

    @property
    def name(self):
        return 'status_rejected'

    @property
    def http_status(self):
        return '422 Unprocessable Entity'


class ProxyRejectedError(BaseError):
    """An :class:`Exception` class that will be raised if user request was
    identified to be an open proxy or public VPN service.
    """

    def message(self, request):
        return 'The IP address has been identified as an open proxy ' +\
            'or VPN service and therefore rejected.'

    @property
    def name(self):
        return 'proxy_rejected'

    @property
    def http_status(self):
        return '422 Unprocessable Entity'


_ERRORS = {
    'rate_limited': RateLimitedError,
    'params_invalid': ParamsInvalidError,
    'akismet_rejected': AkismetRejectedError,
    'dnsbl_rejected': DNSBLRejectedError,
    'ban_rejected': BanRejectedError,
    'status_rejected': StatusRejectedError,
    'proxy_rejected': ProxyRejectedError,
}


def deserialize_error(type_):
    """Deserialize the given error type string into an error class."""
    return _ERRORS.get(type_, BaseError)
