import unittest

from . import ModelSessionMixin


class TestBanModel(ModelSessionMixin, unittest.TestCase):
    def test_listed(self):
        from datetime import datetime, timedelta
        from ..models import Ban

        ban1 = self._make(Ban(ip_address="10.0.1.0/24"))
        ban2 = self._make(Ban(ip_address="10.0.2.0/24"))
        ban3 = self._make(Ban(ip_address="10.0.3.1"))
        ban4 = self._make(Ban(ip_address="10.0.4.0/24", scope="foo:bar"))
        self._make(Ban(ip_address="10.0.5.0/24", active=False))
        self._make(
            Ban(
                ip_address="10.0.6.0/24",
                active_until=datetime.now() - timedelta(days=1),
            )
        )
        self.dbsession.commit()

        def _makeQuery(ip_address, **kwargs):
            return (
                self.dbsession.query(Ban)
                .filter(Ban.listed(ip_address, **kwargs))
                .first()
            )

        self.assertEqual(ban1, _makeQuery("10.0.1.1"))
        self.assertEqual(ban2, _makeQuery("10.0.2.1"))
        self.assertEqual(ban3, _makeQuery("10.0.3.1"))
        self.assertEqual(ban3, _makeQuery("10.0.3.1", scopes=["foo:bar"]))
        self.assertEqual(ban4, _makeQuery("10.0.4.1", scopes=["foo:bar"]))
        self.assertEqual(None, _makeQuery("10.0.4.1"))
        self.assertEqual(None, _makeQuery("10.0.5.1"))
        self.assertEqual(None, _makeQuery("10.0.6.1"))

    def test_duration(self):
        from datetime import datetime, timedelta
        from ..models import Ban

        ban = self._make(
            Ban(
                ip_address="10.0.1.0/24",
                active_until=datetime.now() + timedelta(days=30),
            )
        )
        self.dbsession.commit()
        self.assertEqual(ban.duration, 30)

    def test_duration_no_duration(self):
        from ..models import Ban

        ban = self._make(Ban(ip_address="10.0.1.0/24"))
        self.dbsession.commit()
        self.assertEqual(ban.duration, 0)
