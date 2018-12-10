import pyramid.scripting

from ..errors import StatusRejectedError
from ..interfaces import IFilterService, ITopicCreateService, ITopicQueryService
from ._base import celery, ModelTask


@celery.task(base=ModelTask, bind=True)
def add_topic(
    self, board_slug, title, body, ip_address, payload, _request=None, _registry=None
):
    """Insert a topic to the database.

    :param board_slug: The slug :type:`str` identifying a board.
    :param title: A :type:`str` topic title.
    :param body: A :type:`str` topic body.
    :param ip_address: An IP address of the topic creator.
    :param payload: A request payload containing request metadata.
    """
    with pyramid.scripting.prepare(request=_request, registry=_registry) as env:
        request = env["request"]
        dbsession = request.find_service(name="db")

        filter_svc = request.find_service(IFilterService)
        filter_result = filter_svc.evaluate(
            payload={"body": body, "ip_address": ip_address, **payload}
        )
        if filter_result.rejected_by:
            return "failure", "%s_rejected" % (filter_result.rejected_by,)

        topic_create_svc = request.find_service(ITopicCreateService)
        try:
            topic = topic_create_svc.create(board_slug, title, body, ip_address)
        except StatusRejectedError as e:
            return "failure", e.name, e.status

        dbsession.flush()
        return "topic", topic.id


@celery.task(base=ModelTask, bind=True)
def expire_topics(self, board_slug, _request=None, _registry=None):
    """Expires all outdated topics by the given slug.

    :param board_slug: The slug :type:`str` identifying a board.
    """
    with pyramid.scripting.prepare(request=_request, registry=_registry) as env:
        request = env["request"]
        dbsession = request.find_service(name="db")
        topic_query_svc = request.find_service(ITopicQueryService)

        for topic in topic_query_svc.list_expired_from_board_slug(board_slug):
            topic.status = "expired"
            dbsession.add(topic)

        dbsession.flush()
