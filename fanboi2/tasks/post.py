import pyramid.scripting

from ..errors import StatusRejectedError
from ..interfaces import IFilterService, IPostCreateService
from ._base import celery, ModelTask


@celery.task(base=ModelTask, bind=True)
def add_post(
        self,
        topic_id,
        body,
        bumped,
        ip_address,
        payload={},
        _request=None,
        _registry=None):
    """Insert a post to a topic.

    :param self: A :class:`celery.Task` object.
    :param topic_id: The ID of a topic to add a post to.
    :param body: Content of the post as submitted by the user.
    :param bumped: A :type:`bool` whether to bump the topic.
    :param ip_address: An IP address of the poster.
    :param payload: A request payload containing request metadata.
    """
    with pyramid.scripting.prepare(
            request=_request,
            registry=_registry) as env:
        request = env['request']
        dbsession = request.find_service(name='db')

        filter_svc = request.find_service(IFilterService)
        filter_result = filter_svc.evaluate(payload={
            'body': body,
            'ip_address': ip_address,
            **payload})
        if filter_result.rejected_by:
            return 'failure', "%s_rejected" % (filter_result.rejected_by,)

        post_create_svc = request.find_service(IPostCreateService)
        try:
            post = post_create_svc.create(
                topic_id,
                body,
                bumped,
                ip_address)
        except StatusRejectedError as e:
            return 'failure', e.name, e.status

        dbsession.flush()
        return 'post', post.id
