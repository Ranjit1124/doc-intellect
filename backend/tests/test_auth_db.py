import os
import tempfile
import unittest

from app import db


class AuthDbTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tempdir.name, "test_auth.db")
        db.set_db_path(self.db_path)
        db.init_db()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_create_and_get_user(self):
        user = db.create_user("alice@example.com", "hashed-pass", "Alice")
        self.assertEqual(user["email"], "alice@example.com")
        fetched = db.get_user_by_email("alice@example.com")
        self.assertEqual(fetched["name"], "Alice")

    def test_create_and_fetch_session(self):
        user = db.create_user("bob@example.com", "hashed-pass", "Bob")
        token = db.create_session("token-123", user["id"])
        fetched = db.get_session("token-123")
        self.assertEqual(fetched["user_id"], user["id"])


if __name__ == "__main__":
    unittest.main()
