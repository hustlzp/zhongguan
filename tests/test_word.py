# coding: utf-8
from .suite import BaseSuite


class TestWord(BaseSuite):
    def test_action(self):
        rv = self.client.get('/word/action')
        assert rv.status_code == 200
