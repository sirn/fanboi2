import unittest

from . import ModelSessionMixin


class TestBanModel(ModelSessionMixin, unittest.TestCase):
    def test_duration(self):
        from datetime import timedelta
        from sqlalchemy.sql import func
        from ..models import Ban

        ban = self._make(
            Ban(ip_address="10.0.1.0/24", active_until=func.now() + timedelta(days=30))
        )
        self.dbsession.commit()
        self.assertEqual(ban.duration, 30)

    def test_duration_no_duration(self):
        from ..models import Ban

        ban = self._make(Ban(ip_address="10.0.1.0/24"))
        self.dbsession.commit()
        self.assertEqual(ban.duration, 0)
