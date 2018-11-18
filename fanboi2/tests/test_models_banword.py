import unittest

from . import ModelSessionMixin


class TestBanwordModel(ModelSessionMixin, unittest.TestCase):
    def test_import(self):
        from ..models import Banword

        banword = Banword(expr="foobar")
        self.assertEqual(banword.expr, "foobar")
