from typing import Any, Dict, Optional

import requests

from ..version import __VERSION__
from . import Payload, Services, register_filter

PostData = Optional[Dict[str, Any]]


@register_filter(name="akismet")
class Akismet(object):
    """Basic integration between Pyramid and Akismet."""

    def __init__(self, key: str, services: Services = None):
        self.key = key

    def _api_post(self, name: str, data: PostData = None) -> requests.Response:
        """Make a request to Akismet API and return the response."""
        return requests.post(
            "https://%s.rest.akismet.com/1.1/%s" % (self.key, name),
            headers={"User-Agent": "fanboi2/%s" % __VERSION__},
            data=data,
            timeout=2,
        )

    def should_reject(self, payload: Payload) -> bool:
        """
        Returns :type:`True` if the message is spam. Returns :type:`False`
        if the message was not a spam or Akismet was not configured.
        """
        if self.key:
            try:
                return (
                    self._api_post(
                        "comment-check",
                        data={
                            "comment_content": payload["body"],
                            "blog": payload["application_url"],
                            "user_ip": payload["ip_address"],
                            "user_agent": payload["user_agent"],
                            "referrer": payload["referrer"],
                        },
                    ).content
                    == b"true"
                )
            except (KeyError, requests.Timeout):
                pass
        return False
