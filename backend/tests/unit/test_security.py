"""Unit tests for app.core.security — no DB, no network."""
import pytest
from app.core.security import get_password_hash, verify_password, generate_api_key, hash_api_key

@pytest.mark.unit
class TestPasswordHashing:
    def test_hash_differs_from_plaintext(self):
        assert get_password_hash("secret") != "secret"

    def test_correct_password_verifies(self):
        h = get_password_hash("secret")
        assert verify_password("secret", h) is True

    def test_wrong_password_fails(self):
        h = get_password_hash("secret")
        assert verify_password("wrong", h) is False

    def test_same_password_different_hashes(self):
        assert get_password_hash("secret") != get_password_hash("secret")

@pytest.mark.unit
class TestApiKey:
    def test_key_has_rag_prefix(self):
        raw, _ = generate_api_key()
        assert raw.startswith("rag_")

    def test_hash_is_deterministic(self):
        raw, _ = generate_api_key()
        assert hash_api_key(raw) == hash_api_key(raw)

    def test_different_keys_different_hashes(self):
        k1, _ = generate_api_key()
        k2, _ = generate_api_key()
        assert hash_api_key(k1) != hash_api_key(k2)
