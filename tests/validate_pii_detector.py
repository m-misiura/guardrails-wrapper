import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apps.pii_app import create_app


class ValidateTextTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()

    def test_validate_text_pass(self):
        response = self.app.post("/validate", json={"text": "This is a safe text."})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Validation passed", response.get_json()["result"])

    def test_validate_text_fail(self):
        response = self.app.post("/validate", json={"text": "Email: test@example.com"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Validation failed", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
