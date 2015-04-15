def serialize_error(type, *args):
    """Serialize the given error type string into an error class.
    If :param:`attrs` is provided, it will be passed to the class on
    initialization.
    """
    return {
        'rate_limited': RateLimitedError,
        'form_invalid': FormInvalidError,
        'spam_blocked': SpamBlockedError,
        'dnsbl_blocked': DnsblBlockedError,
        'status_blocked': StatusBlockedError,
    }.get(type, BaseError)(*args)


class BaseError(Exception):
    pass


class RateLimitedError(BaseError):
    """An :class:`Exception` class that will be raised if user request was
    blocked due to rate limiter. The time left until user is unblocked could
    be accessed from :property:`timeleft`.

    :param timeleft: An :type:`int` in seconds until user is unblocked.
    :type timeleft: int
    """

    def __init__(self, timeleft):
        self.timeleft = timeleft


class FormInvalidError(BaseError):
    """An :class:`Exception` class that will be raised if user request could
    not be processed due to form being invalid. Error messages are stored
    inside :property:`messages`.

    :param messages: An :type:`dict` of :type:`list` of field errors.
    :type messages: str
    """

    def __init__(self, messages):
        self.messages = messages


class SpamBlockedError(BaseError):
    """An :class:`Exception` class that will be raised if user request was
    blocked due user request failed a spam check.
    """
    pass


class DnsblBlockedError(BaseError):
    """An :class:`Exception` class that will be raised if user request was
    blocked due user IP address failed an DNSBL check.
    """
    pass


class StatusBlockedError(BaseError):
    """An :class:`Exception` class that will be raised if user request was
    blocked due the topic or the board being locked. The status that caused
    the lock could be retrieved from :property:`status`.

    :param status: A :type:`str` of the status that caused the block.
    :type status: str
    """

    def __init__(self, status):
        self.status = status
