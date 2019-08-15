import re

from enum import Enum
from lark import Lark, Transformer


class ScopeType(Enum):
    STRING = 1
    REGEXP = 2


class _Transformer(Transformer):
    def scope(self, item):
        if not item:
            return None
        return item[0]

    def pair(self, item):
        key, value = item
        return str(key), value

    def key(self, item):
        return str(item[0])

    def value(self, item):
        if not item:
            return None
        token_type = item[0].type
        if token_type == "REGEXP":
            return (ScopeType.REGEXP, str(item[0][1:-1]))
        elif token_type == "ESCAPED_STRING":
            return (ScopeType.STRING, str(item[0][1:-1]))
        return (ScopeType.STRING, str(item[0]))


SCOPE_PARSER = Lark(
    r"""
    scope   : pair?
    pair    : KEYWORD ":" value
    value   : REGEXP | ESCAPED_STRING | STRING?

    KEYWORD : (LETTER | "_" | "-")+
    REGEXP  : "/" ("\\\""|/[^"]/)* "/"
    STRING  : /[^" \t\f\r\n]/+

    %import common.ESCAPED_STRING -> ESCAPED_STRING
    %import common.LETTER         -> LETTER
    """,
    start="scope",
    parser="lalr",
    transformer=_Transformer(),
)


class ScopeService(object):
    """Scope service provides a service for evaluating a scope by the given serialized
    object data and a scope rules.
    """

    def evaluate(self, scope, obj):
        """Evaluates whether the given :param:`obj` matches the given :param:`scope`.
        Always return :type:`True` if scope value is empty. Scope must be one of the
        following formats:

        * ``key:`` checks if the given key exists.
        * ``key:value`` checks if the given key and value pair exists.
        * ``key:"value with space"`` similar to ``key:value`` but allow space.
        * ``key:/regex/`` checks if the given key matches the given regular expression.

        :param scope: Scope to evaluate.
        :param obj: A :type:`dict` to evaluate for.
        """

        # Always return True if scope is not present i.e. unscoped.
        p_scope = SCOPE_PARSER.parse(scope)
        if not p_scope:
            return True

        key, predicate = p_scope
        if key in obj:
            # Returns True if scope key is present but not the value, e.g. "foo:"
            # This is used for key-checking.
            if not predicate:
                return True

            # Returns true if regexp matches, e.g. "foo:/bar/"
            p_kind, p_value = predicate
            if p_kind == ScopeType.REGEXP:
                p_re = re.compile(p_value)
                if p_re.search(obj[key]):
                    return True

            # Returns true if value matches, e.g. "foo:bar"
            elif p_kind == ScopeType.STRING:
                if p_value == obj[key]:
                    return True

        return False
