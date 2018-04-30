from celery import states

from ..errors import deserialize_error
from ..models import deserialize_model


class ResultProxy(object):
    """A proxy class for :class:`celery.result.AsyncResult` that provide
    results serialization using :func:`fanboi2.errors.deserialize_error` and
    :func:`fanboi2.models.deserialize_model`.

    :param result: A result of :class:`celery.AsyncResult`.
    """

    def __init__(self, result):
        self._result = result
        self._object = None

    def deserialize(self, request):
        """Deserializing the result into Python object."""
        if self._object is None:
            obj, id_, *args = self._result.get()
            if obj == 'failure':
                class_ = deserialize_error(id_)
                if class_ is not None:
                    self._object = class_(*args)
            else:
                dbsession = request.find_service(name='db')
                class_ = deserialize_model(obj)
                if class_ is not None:
                    self._object = dbsession.query(class_).get(id_)
        return self._object

    def success(self):
        """Returns true if result was successfully processed."""
        return self._result.state == states.SUCCESS

    def __getattr__(self, name):
        return self._result.__getattribute__(name)
