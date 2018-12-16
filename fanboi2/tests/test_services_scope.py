import unittest


class TestScopeServiceParser(unittest.TestCase):
    def _make_one(self):
        from ..services.scope import SCOPE_PARSER

        return SCOPE_PARSER

    def test_parse(self):
        from ..services.scope import ScopeType

        p = self._make_one()
        self.assertEqual(p.parse(""), None)
        self.assertEqual(p.parse("foo:"), ("foo", None))
        self.assertEqual(p.parse("foo:ภาษา"), ("foo", (ScopeType.STRING, "ภาษา")))
        self.assertEqual(p.parse("foo:bar"), ("foo", (ScopeType.STRING, "bar")))
        self.assertEqual(p.parse('foo:"ba r"'), ("foo", (ScopeType.STRING, "ba r")))
        self.assertEqual(p.parse("foo:/(?i)Aa/"), ("foo", (ScopeType.REGEXP, "(?i)Aa")))
        self.assertEqual(p.parse("foo:/ไทย/"), ("foo", (ScopeType.REGEXP, "ไทย")))
        self.assertEqual(p.parse("foo://"), ("foo", (ScopeType.REGEXP, "")))

    def test_parse_errors(self):
        from lark.exceptions import LarkError

        p = self._make_one()
        with self.assertRaises(LarkError):
            p.parse(":bar")
        with self.assertRaises(LarkError):
            p.parse("foo:bar baz")


class TestScopeService(unittest.TestCase):
    def _get_target_class(self):
        from ..services import ScopeService

        return ScopeService

    def test_evaluate(self):
        scope_svc = self._get_target_class()()
        obj = {"board": "foo", "title": "hello world", "key": "value"}
        self.assertTrue(scope_svc.evaluate("board:foo", obj))
        self.assertTrue(scope_svc.evaluate("board:", obj))
        self.assertTrue(scope_svc.evaluate("key:value", obj))
        self.assertTrue(scope_svc.evaluate('title:"hello world"', obj))
        self.assertTrue(scope_svc.evaluate("title:/(?i)Ello/", obj))
        self.assertTrue(scope_svc.evaluate("title://", obj))
        self.assertFalse(scope_svc.evaluate("foo:", obj))
        self.assertFalse(scope_svc.evaluate("board:bar", obj))
        self.assertFalse(scope_svc.evaluate("key:valuez", obj))
        self.assertFalse(scope_svc.evaluate("title:/Ello/", obj))
