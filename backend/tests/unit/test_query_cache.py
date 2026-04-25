"""Unit tests for app.core.query_cache — mocked Redis."""
import pytest
from app.core.query_cache import RedisQueryCache

@pytest.mark.unit
class TestCacheKey:
    def setup_method(self):
        self.cache = RedisQueryCache.__new__(RedisQueryCache)
        self.cache._lru = {}

    def test_same_inputs_same_key(self):
        k1 = self.cache._make_key(user_id=1, project_id=10, query="hello")
        k2 = self.cache._make_key(user_id=1, project_id=10, query="hello")
        assert k1 == k2

    def test_different_users_different_keys(self):
        k1 = self.cache._make_key(user_id=1, project_id=10, query="hello")
        k2 = self.cache._make_key(user_id=2, project_id=10, query="hello")
        assert k1 != k2

    def test_different_projects_different_keys(self):
        k1 = self.cache._make_key(user_id=1, project_id=10, query="hello")
        k2 = self.cache._make_key(user_id=1, project_id=99, query="hello")
        assert k1 != k2

    def test_case_normalized(self):
        k1 = self.cache._make_key(user_id=1, project_id=1, query="Hello")
        k2 = self.cache._make_key(user_id=1, project_id=1, query="hello")
        assert k1 == k2

    def test_whitespace_normalized(self):
        k1 = self.cache._make_key(user_id=1, project_id=1, query="  hello  ")
        k2 = self.cache._make_key(user_id=1, project_id=1, query="hello")
        assert k1 == k2
