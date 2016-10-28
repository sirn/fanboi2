from sqlalchemy.orm import column_property
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from ._base import JsonType
from .rule import Rule


class RuleOverride(Rule):
    """Model class that provides a settings override on top of rule model."""

    __tablename__ = 'rule_override'
    __mapper_args__ = {'polymorphic_identity': 'override'}

    rule_id = Column(Integer, ForeignKey('rule.id'), primary_key=True)
    override = Column(JsonType, default={})
