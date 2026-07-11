import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient


class PersistenceTests(unittest.TestCase):
    def test_signup_persists_to_disk_between_reloads(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "activities.json"
            os.environ["ACTIVITIES_DATA_FILE"] = str(data_file)

            import src.app as app_module

            app_module = importlib.reload(app_module)
            client = TestClient(app_module.app)

            response = client.post(
                "/activities/Chess Club/signup?email=test.student@mergington.edu"
            )
            self.assertEqual(response.status_code, 200)

            with data_file.open("r", encoding="utf-8") as handle:
                saved_data = json.load(handle)

            self.assertIn(
                "test.student@mergington.edu",
                saved_data["Chess Club"]["participants"],
            )

            reloaded_module = importlib.reload(app_module)
            reloaded_client = TestClient(reloaded_module.app)
            reload_response = reloaded_client.get("/activities")
            self.assertEqual(reload_response.status_code, 200)
            self.assertIn(
                "test.student@mergington.edu",
                reload_response.json()["Chess Club"]["participants"],
            )


if __name__ == "__main__":
    unittest.main()
