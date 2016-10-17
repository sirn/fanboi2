from ._base import DBSession, Base, JsonType
from ._identity import Identity
from ._redis_proxy import RedisProxy
from .board import Board
from .topic import Topic
from .post import Post


redis_conn = RedisProxy()
identity = Identity(redis=redis_conn)


_MODELS = {
    'board': Board,
    'topic': Topic,
    'post': Post,
}


def serialize_model(type_):
    return _MODELS.get(type_)
