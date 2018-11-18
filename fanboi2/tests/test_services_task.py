import unittest
import unittest.mock


class TestTaskQueryService(unittest.TestCase):
    @unittest.mock.patch("fanboi2.tasks.celery.AsyncResult")
    def test_result_from_uid(self, result_):
        from ..services import TaskQueryService
        from . import DummyAsyncResult

        result_.return_value = async_result = DummyAsyncResult("dummy", "success", "yo")
        task_query_svc = TaskQueryService()
        self.assertEqual(task_query_svc.result_from_uid("dummy")._result, async_result)
