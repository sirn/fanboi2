from sqlalchemy.sql.sqltypes import Enum


BoardStatusEnum = Enum("open", "restricted", "locked", "archived", name="board_status")


IdentTypeEnum = Enum("none", "ident", "ident_v6", "ident_admin", name="ident_type")


TopicStatusEnum = Enum("open", "locked", "archived", "expired", name="topic_status")
