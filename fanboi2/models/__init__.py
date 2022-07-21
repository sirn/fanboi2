from ._base import Base
from ._versioned import setup_versioned, make_history_event
from .ban import Ban
from .banword import Banword
from .board import Board
from .group import Group
from .page import Page
from .post import Post
from .setting import Setting
from .topic import Topic
from .topic_meta import TopicMeta
from .user import User
from .user_session import UserSession


__all__ = [
    "Base",
    "Ban",
    "Banword",
    "Board",
    "Group",
    "Page",
    "Post",
    "Setting",
    "Topic",
    "TopicMeta",
    "User",
    "UserSession",
    "setup_versioned",
    "make_history_event",
]


_MODELS = {
    "ban": Ban,
    "banword": Banword,
    "board": Board,
    "group": Group,
    "page": Page,
    "post": Post,
    "setting": Setting,
    "topic": Topic,
    "topic_meta": TopicMeta,
    "user": User,
    "user_session": UserSession,
}


# Versioned need to be setup after all models are initialized otherwise
# SQLAlchemy won't be able to locate relation tables due to import order.
setup_versioned()


def deserialize_model(type_):
    """Deserialize the given model type string into a model class."""
    return _MODELS.get(type_)
