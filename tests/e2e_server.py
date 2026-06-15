import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TEST_DATA = tempfile.TemporaryDirectory(prefix="decants-e2e-")
os.environ["PORT"] = "8765"
os.environ["DECANTS_DB_PATH"] = str(Path(TEST_DATA.name) / "e2e.sqlite3")
os.environ["DECANTS_UPLOAD_DIR"] = str(Path(TEST_DATA.name) / "uploads")
os.environ["DECANTS_ENV"] = "development"
os.environ["DECANTS_ADMIN_USER"] = "admin@example.com"
os.environ["DECANTS_ADMIN_PASSWORD"] = "SenhaE2E123!"
os.environ["DECANTS_SECRET_KEY"] = "e2e-secret-key-with-at-least-32-characters"

import server


server.main()
