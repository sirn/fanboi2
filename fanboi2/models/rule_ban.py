from sqlalchemy.orm import column_property
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from .rule import Rule


class RuleBan(Rule):
    """Model class that provides a banlist on top of rule model."""

    __tablename__ = 'rule_ban'
    __mapper_args__ = {'polymorphic_identity': 'ban'}

    rule_id = Column(Integer, ForeignKey('rule.id'), primary_key=True)
